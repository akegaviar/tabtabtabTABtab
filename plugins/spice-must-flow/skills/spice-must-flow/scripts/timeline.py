#!/usr/bin/env python3
"""Timeline visualization v2 for spice-must-flow.

Session-based, proportional-width, interleaved User/Claude visualization.
- Sessions separated by 10+ min gaps
- Single row per session with interleaved blocks
- Width proportional to duration
- Characters: ░ (User), █ (Claude <2min), ▓ (Claude >2min drift risk)
"""
import json
import os
import re
import subprocess
import sys
from datetime import datetime, timezone, timedelta
from pathlib import Path

# Constants
SESSION_GAP_THRESHOLD = 600  # 10 minutes = new session
LINE_WIDTH = 70  # chars before wrapping

# Characters
CHAR_USER = '░'
CHAR_CLAUDE = '█'


def get_last_content_timestamp(filepath):
    """Read last timestamp from JSONL file using efficient seek-to-end."""
    try:
        with open(filepath, 'rb') as f:
            f.seek(0, 2)
            pos = f.tell()
            chunk_size = 4096
            while pos > 0:
                read_size = min(chunk_size, pos)
                pos = max(0, pos - chunk_size)
                f.seek(pos)
                chunk = f.read(read_size)
                lines = chunk.split(b'\n')
                for line in reversed(lines):
                    if line.strip():
                        try:
                            data = json.loads(line)
                            ts = data.get('timestamp')
                            if ts:
                                return ts
                        except:
                            pass
        return ''
    except:
        return ''


def load_index_timestamps(base_path):
    """Load session timestamps from sessions-index.json."""
    index_path = os.path.join(base_path, 'sessions-index.json')
    timestamps = {}
    try:
        with open(index_path, 'r') as f:
            data = json.load(f)
            for entry in data.get('entries', []):
                sid = entry.get('sessionId', '')
                modified = entry.get('modified', '')
                if sid and modified:
                    timestamps[sid] = modified
    except:
        pass
    return timestamps


def is_companion_session(filepath):
    """Check if session is a companion by looking for the actual welcome message.

    Looks for the specific welcome pattern to avoid false positives when
    markers appear in documentation or discussions about spice-must-flow.
    """
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(8000)
            # Must have the actual welcome message
            return '༼🌀🌀༽ Spice flow connected.' in content
    except:
        return False


def parse_ts(ts):
    """Parse ISO timestamp to datetime."""
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except:
        return None


def extract_entries_with_roles(filepath, worktree=None):
    """Extract entries with timestamp, role, and worktree (user/assistant only)."""
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            for line in f:
                line = line.strip()
                if not line:
                    continue
                try:
                    e = json.loads(line)
                    ts = e.get("timestamp", "")
                    t = e.get("type")
                    if t == "user":
                        entries.append((ts, "user", worktree))
                    elif t == "assistant":
                        entries.append((ts, "assistant", worktree))
                except:
                    pass
    except:
        pass
    return entries


def format_duration(seconds):
    """Format duration for display."""
    if seconds < 60:
        return f"{int(seconds)}s"
    minutes = seconds / 60
    if minutes < 60:
        return f"{int(minutes)}m"
    hours = minutes / 60
    if hours < 24:
        if hours == int(hours):
            return f"{int(hours)}h"
        return f"{hours:.1f}h"
    days = hours / 24
    return f"{days:.1f}d"


def format_time(dt):
    """Format datetime as HH:MM in local time."""
    return dt.astimezone().strftime("%H:%M")


def build_segments(entries):
    """Build segments from entries.

    Returns list of (role, duration_seconds, start_dt, end_dt, is_real_exchange, worktree).
    role is 'user' or 'claude'.
    is_real_exchange is True only for user->assistant transitions (actual exchanges).
    worktree is the label of the worktree the entry came from.
    """
    segments = []

    for i in range(len(entries) - 1):
        ts1, role1, wt1 = entries[i]
        ts2, role2, wt2 = entries[i + 1]

        dt1 = parse_ts(ts1)
        dt2 = parse_ts(ts2)

        if not dt1 or not dt2:
            continue

        duration = (dt2 - dt1).total_seconds()
        if duration < 0:
            continue

        # Who was active during this gap?
        # user message -> assistant response = Claude was working (real exchange)
        # assistant response -> user message = User was reading/thinking/typing
        # user -> user or assistant -> assistant = spurious (hooks, tool calls, etc.)
        if role1 == "user":
            is_real_exchange = (role2 == "assistant")
            segments.append(("claude", duration, dt1, dt2, is_real_exchange, wt1))
        else:
            segments.append(("user", duration, dt1, dt2, False, wt1))

    return segments


def split_into_sessions(segments):
    """Split segments into sessions based on 10+ min gaps.

    Returns list of sessions, where each session is a list of segments.
    """
    if not segments:
        return []

    sessions = []
    current_session = [segments[0]]

    for i in range(1, len(segments)):
        prev_seg = segments[i - 1]
        curr_seg = segments[i]

        # Check gap between end of previous and start of current
        gap = (curr_seg[2] - prev_seg[3]).total_seconds()

        # Also check if this segment itself is a user gap > threshold
        # (user was away for 10+ min)
        if curr_seg[0] == "user" and curr_seg[1] >= SESSION_GAP_THRESHOLD:
            # End current session, start new one after this gap
            if current_session:
                sessions.append(current_session)
            current_session = []
            continue

        if gap >= SESSION_GAP_THRESHOLD:
            # Gap too large, start new session
            if current_session:
                sessions.append(current_session)
            current_session = [curr_seg]
        else:
            current_session.append(curr_seg)

    if current_session:
        sessions.append(current_session)

    return sessions


def get_resolution(total_seconds):
    """Determine seconds per character based on session duration."""
    minutes = total_seconds / 60
    if minutes < 30:
        return 15  # 1 char = 15 seconds
    elif minutes < 120:
        return 30  # 1 char = 30 seconds
    else:
        return 60  # 1 char = 1 minute


def render_session(segments, line_width=LINE_WIDTH, show_worktree=False):
    """Render a single session as interleaved proportional blocks.

    Returns list of strings (lines).
    """
    if not segments:
        return []

    # Calculate session stats
    total_seconds = sum(s[1] for s in segments)
    claude_seconds = sum(s[1] for s in segments if s[0] == "claude")
    # Only count real exchanges (user->assistant), not spurious user->user transitions
    exchange_count = sum(1 for s in segments if s[0] == "claude" and s[4])

    start_dt = segments[0][2]
    end_dt = segments[-1][3]

    # Collect worktrees in this session
    worktrees = set(s[5] for s in segments if s[5])

    # Calculate Claude percentage
    claude_pct = int((claude_seconds / total_seconds) * 100) if total_seconds > 0 else 0

    # Build header
    time_range = f"{format_time(start_dt)}-{format_time(end_dt)}"
    duration = format_duration(total_seconds)
    header = f"{time_range} | {duration} | {exchange_count} exchanges | Claude {claude_pct}%"

    # Add worktree info if multiple worktrees exist
    if show_worktree and worktrees:
        wt_str = ",".join(sorted(worktrees))
        header = f"{header} [{wt_str}]"

    # Determine resolution
    seconds_per_char = get_resolution(total_seconds)

    # Build character string
    chars = []
    for role, seg_duration, _, _, _, _ in segments:
        num_chars = max(1, int(seg_duration / seconds_per_char))
        char = CHAR_USER if role == "user" else CHAR_CLAUDE
        chars.extend([char] * num_chars)

    # Wrap into lines
    lines = [header]
    for i in range(0, len(chars), line_width):
        line_chars = chars[i:i + line_width]
        lines.append(''.join(line_chars))

    return lines


def render_timeline(sessions, mode="t"):
    """Render all sessions as timeline visualization."""
    if not sessions:
        return f"{mode} (no activity)"

    # Calculate totals
    all_segments = [seg for session in sessions for seg in session]
    total_seconds = sum(s[1] for s in all_segments)
    claude_seconds = sum(s[1] for s in all_segments if s[0] == "claude")
    session_count = len(sessions)

    # Collect all worktrees
    all_worktrees = set(s[5] for s in all_segments if s[5])
    show_worktree = len(all_worktrees) > 1

    # Get date range for t+
    first_date = sessions[0][0][2].astimezone().date()
    last_date = sessions[-1][-1][3].astimezone().date()

    # Build output
    output = []

    # Top summary
    if mode == "t+":
        date_range = f"{first_date.strftime('%b %d')} - {last_date.strftime('%b %d')}"
        summary = f"{mode} | {date_range} | {format_duration(total_seconds)} | {format_duration(claude_seconds)} Claude | {session_count} sessions"
    else:
        summary = f"{mode} | {format_duration(total_seconds)} | {format_duration(claude_seconds)} Claude | {session_count} sessions"

    # Add worktrees indicator if multiple
    if show_worktree:
        summary = f"{summary} | worktrees: {','.join(sorted(all_worktrees))}"

    output.append(summary)
    output.append("")

    # Render each session, with date headers for t+
    current_date = None
    for session in sessions:
        session_date = session[0][2].astimezone().date()

        # Add date header if date changed (only for t+)
        if mode == "t+" and session_date != current_date:
            if current_date is not None:
                output.append("")  # Extra spacing between days
            output.append(f"── {session_date.strftime('%b %d, %a')} ──")
            current_date = session_date

        session_lines = render_session(session, show_worktree=show_worktree)
        output.extend(session_lines)
        output.append("")

    return "\n".join(output)


def get_session_base_paths(include_worktrees=False):
    """Get session directories for current project and optionally related git worktrees.

    Args:
        include_worktrees: If True, include all related git worktrees. If False (default),
                          only include the current directory's sessions.

    Returns dict mapping session_dir -> worktree_label (branch name or dir basename).
    """
    home = Path.home()
    cwd = os.getcwd()

    def path_to_session_dir(path):
        return str(home / ".claude/projects" / path.replace("/", "-"))

    # Map worktree_path -> branch_name
    worktrees = {}

    # Only scan for related worktrees if explicitly requested
    if include_worktrees:
        try:
            result = subprocess.run(
                ['git', 'worktree', 'list', '--porcelain'],
                capture_output=True, text=True, timeout=5,
                cwd=cwd
            )
            if result.returncode == 0:
                current_wt = None
                for line in result.stdout.split('\n'):
                    if line.startswith('worktree '):
                        current_wt = line[9:]
                    elif line.startswith('branch ') and current_wt:
                        # Extract branch name from refs/heads/branch-name
                        branch = line[7:]
                        if branch.startswith('refs/heads/'):
                            branch = branch[11:]
                        worktrees[current_wt] = branch
                    elif line == '' and current_wt:
                        # End of worktree entry - if no branch, use dir basename
                        if current_wt not in worktrees:
                            worktrees[current_wt] = os.path.basename(current_wt)
                        current_wt = None
                # Handle last entry
                if current_wt and current_wt not in worktrees:
                    worktrees[current_wt] = os.path.basename(current_wt)
        except Exception:
            pass  # Not a git repo or git not available

    # If no worktrees found or not scanning worktrees, use current dir only
    if not worktrees:
        worktrees[cwd] = os.path.basename(cwd)

    # Convert to session directories and filter to existing ones
    session_dirs = {}
    for wt_path, label in worktrees.items():
        session_dir = path_to_session_dir(wt_path)
        if os.path.isdir(session_dir):
            session_dirs[session_dir] = label

    return session_dirs


def main():
    if len(sys.argv) < 2:
        print("t (no input)")
        sys.exit(0)

    user_input = sys.argv[1].strip()
    all_time = "+" in user_input or user_input == "t+"
    include_worktrees = 'w' in user_input.lower()

    # Get session directories (current project, optionally + related worktrees)
    base_paths = get_session_base_paths(include_worktrees=include_worktrees)  # dict: session_dir -> worktree_label
    if not base_paths:
        print("t (no project sessions)")
        sys.exit(0)

    # Find session files from all directories
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$')
    session_files = []
    file_to_worktree = {}  # Map session file -> worktree label
    index_timestamps = {}

    for base_path, wt_label in base_paths.items():
        # Load index timestamps from this directory
        index_timestamps.update(load_index_timestamps(base_path))

        # Find session files
        try:
            all_files = os.listdir(base_path)
            for f in all_files:
                if uuid_pattern.match(f):
                    filepath = os.path.join(base_path, f)
                    session_files.append(filepath)
                    file_to_worktree[filepath] = wt_label
        except OSError:
            continue

    # Filter companion sessions
    session_files = [f for f in session_files if not is_companion_session(f)]

    if not session_files:
        print("t (no sessions)")
        sys.exit(0)

    # Sort by timestamp
    def get_content_timestamp(filepath):
        session_id = os.path.basename(filepath).replace('.jsonl', '')
        if session_id in index_timestamps:
            return index_timestamps[session_id]
        return get_last_content_timestamp(filepath)

    session_files.sort(key=get_content_timestamp)

    # Extract all entries
    all_entries = []

    for session_file in session_files:
        wt_label = file_to_worktree.get(session_file)
        entries = extract_entries_with_roles(session_file, wt_label)
        if entries:
            all_entries.extend(entries)

    # Sort chronologically
    all_entries.sort(key=lambda x: x[0])

    # Filter for today if not all_time
    if not all_time:
        today = datetime.now().date()
        filtered = []
        for ts, role, wt in all_entries:
            dt = parse_ts(ts)
            if dt and dt.astimezone().date() == today:
                filtered.append((ts, role, wt))
        all_entries = filtered

        if not all_entries:
            print("t (no activity today)")
            sys.exit(0)

    if len(all_entries) < 2:
        print("t (not enough entries)")
        sys.exit(0)

    # Build segments
    segments = build_segments(all_entries)

    if not segments:
        print("t (no activity to visualize)")
        sys.exit(0)

    # Split into sessions (10+ min gap = new session)
    sessions = split_into_sessions(segments)

    if not sessions:
        print("t (no sessions to visualize)")
        sys.exit(0)

    # Render
    mode = "t+" if all_time else "t"
    output = render_timeline(sessions, mode=mode)

    print(output)


if __name__ == "__main__":
    main()
