#!/usr/bin/env python3
"""spice_must_flow preprocessor - reads session transcripts and outputs formatted entries."""
import json, os, random, re, subprocess, sys
from datetime import datetime, timezone
from pathlib import Path


def get_last_content_timestamp(filepath):
    """Read last timestamp from JSONL file using efficient seek-to-end."""
    try:
        with open(filepath, 'rb') as f:
            f.seek(0, 2)  # Seek to end
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
        print("[!] Usage: preprocessor.py 'USER_INPUT'")
        sys.exit(1)

    user_input = sys.argv[1]
    home = Path.home()

    # Parse user input
    rewind_minutes = user_input.count('<') * 10
    comma_count = user_input.count(',')
    all_history = ',+' in user_input
    entry_limit = 0 if all_history else (comma_count * 100 if comma_count > 0 else 30)
    include_expanded = '^' in user_input
    include_worktrees = 'w' in user_input.lower()

    # Detect buttons
    buttons = []
    inp = user_input.lower()
    if 'help' in inp:
        buttons.append('help')
    else:
        dot_count = user_input.count('.')
        if dot_count == 1: buttons.append('.')
        elif dot_count == 2: buttons.append('..')
        elif dot_count >= 3: buttons.append('...')
        if 'x' in inp: buttons.append('x')
        if '-' in user_input and ',-' not in user_input: buttons.append('-')
        if '>' in inp: buttons.append('>')
        if rewind_minutes > 0: buttons.append('<')
        if '~' in inp: buttons.append('~')
        if '#' in inp: buttons.append('#')
        if 'q' in inp: buttons.append('q')
        if 'p' in inp and 'help' not in inp: buttons.append('p')
        # Random button - pick from available buttons
        if 'r' in inp:
            random_choices = ['.', '..', '...', 'x', '-', '>', '~', '#', 'q', 'p']
            buttons.append(random.choice(random_choices))

    # Get session directories (current project, optionally + related worktrees)
    base_paths = get_session_base_paths(include_worktrees=include_worktrees)
    if not base_paths:
        print("[!] Project directory not found")
        sys.exit(1)

    # Filter companion sessions
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

    # Check if multiple worktrees have sessions
    all_worktrees = set(file_to_worktree.values())
    show_worktree = len(all_worktrees) > 1

    # Hybrid timestamp sorting: use index for cached timestamps, last-line read for new sessions
    def get_content_timestamp(filepath):
        """Get content timestamp: index first, then last-line fallback."""
        session_id = os.path.basename(filepath).replace('.jsonl', '')
        if session_id in index_timestamps:
            return index_timestamps[session_id]
        return get_last_content_timestamp(filepath)

    session_files.sort(key=get_content_timestamp, reverse=True)

    entries = []
    scanned_sessions = []
    session_ids = set()

    def parse_ts(ts):
        if not ts: return None
        try: return datetime.fromisoformat(ts.replace("Z", "+00:00"))
        except: return None

    def extract_entries(filepath, source="main", worktree=None):
        try:
            with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                for line in f:
                    line = line.strip()
                    if not line: continue
                    try:
                        e = json.loads(line)
                        ts = e.get("timestamp", "")
                        t = e.get("type")
                        if t == "user":
                            c = e.get("message", {}).get("content", "")
                            if isinstance(c, str) and c.strip():
                                if "<command-name>" not in c[:50]:
                                    entries.append((ts, "U", c, source, worktree))
                            elif isinstance(c, list):
                                for item in c:
                                    if item.get("type") == "text":
                                        entries.append((ts, "U", item.get("text", ""), source, worktree))
                                    elif item.get("type") == "tool_result":
                                        content = item.get("content", "")
                                        if isinstance(content, list):
                                            content = " ".join(
                                                block.get("text", str(block)) if isinstance(block, dict) else str(block)
                                                for block in content
                                            )
                                        entries.append((ts, "R", content, source, worktree))
                        elif t == "assistant":
                            for b in e.get("message", {}).get("content", []) or []:
                                if b.get("type") == "text":
                                    entries.append((ts, "A", b.get("text", ""), source, worktree))
                                elif b.get("type") == "tool_use":
                                    n = b.get("name", "")
                                    i = str(b.get("input", {}))
                                    entries.append((ts, "T", f"{n}: {i}", source, worktree))
                    except: pass
        except: pass

    # Adaptive scanning
    target = entry_limit * 3 if entry_limit > 0 and not all_history else 0

    for session_file in session_files:
        if is_companion_session(session_file):
            continue
        scanned_sessions.append(session_file)
        session_ids.add(os.path.basename(session_file).replace('.jsonl', ''))
        wt_label = file_to_worktree.get(session_file)
        extract_entries(session_file, "main", wt_label)
        if target > 0 and len(entries) >= target:
            break

    # Expanded mode
    if include_expanded:
        for base_path, wt_label in base_paths.items():
            try:
                all_files = os.listdir(base_path)
                for f in all_files:
                    if f.startswith("agent-") and f.endswith(".jsonl"):
                        extract_entries(os.path.join(base_path, f), "agent", wt_label)
            except OSError:
                continue
        for sid in session_ids:
            for base_path, wt_label in base_paths.items():
                tool_results_dir = os.path.join(base_path, sid, "tool-results")
                if os.path.isdir(tool_results_dir):
                    for f in os.listdir(tool_results_dir):
                        if f.endswith(".txt"):
                            tr_file = os.path.join(tool_results_dir, f)
                            try:
                                mtime = os.path.getmtime(tr_file)
                                ts = datetime.fromtimestamp(mtime, timezone.utc).isoformat()
                                with open(tr_file, 'r', encoding='utf-8', errors='ignore') as fh:
                                    content = fh.read()
                                entries.append((ts, "R", f"[tool-result] {content}", "tool", wt_label))
                            except: pass

    entries.sort(key=lambda x: x[0])
    total_entries = len(entries)
    now = datetime.now(timezone.utc)

    if rewind_minutes > 0:
        rewind_start = now.timestamp() - (rewind_minutes * 60)
        filtered = []
        for ts, role, text, source, wt in entries:
            ts_dt = parse_ts(ts)
            if ts_dt and ts_dt.timestamp() >= rewind_start:
                filtered.append((ts, role, text, source, wt))
        entries = filtered[-entry_limit:] if entry_limit > 0 else filtered
        print(f"=== LAST {rewind_minutes}min ===")
    else:
        entries = entries[-entry_limit:] if entry_limit > 0 else entries

    # Plan detection
    write_plan_pattern = re.compile(r"^Write: \{'file_path': '[^']*\.claude/plans/([^'/]+\.md)'")
    detected_plans = {}
    for ts, role, text, source, wt in entries:
        if role == "T":
            match = write_plan_pattern.match(text)
            if match:
                slug = match.group(1)
                if slug not in detected_plans:
                    detected_plans[slug] = ts

    project_plans_dir = Path.cwd() / ".claude" / "plans"
    if project_plans_dir.exists():
        for pf in project_plans_dir.glob("*.md"):
            if pf.name not in detected_plans:
                detected_plans[pf.name] = "project-scope"

    # Output
    if buttons:
        print(f"[buttons: {' '.join(buttons)}]")

    if detected_plans:
        print(f"[plans:{len(detected_plans)}]")
        for slug in sorted(detected_plans.keys()):
            plan_path = home / ".claude/plans" / slug
            if not plan_path.exists() and project_plans_dir.exists():
                plan_path = project_plans_dir / slug
            if plan_path.exists():
                try:
                    content = plan_path.read_text()
                    title_match = re.search(r'^#\s+(.+)$', content, re.MULTILINE)
                    title = title_match.group(1) if title_match else slug
                    print(f"[P:{slug}] {title}")
                except: pass

    # Stats
    shown = len(entries)
    coverage_pct = (shown / total_entries * 100) if total_entries > 0 else 100
    total_sessions = len([f for f in session_files if not is_companion_session(f)])
    session_info = f"{len(scanned_sessions)}/{total_sessions}s" if len(scanned_sessions) < total_sessions else (f"{total_sessions}s" if total_sessions > 1 else "")

    sources = set(e[3] for e in entries)
    source_info = f"+{'+'.join(s[0] for s in sorted(sources) if s != 'main')}" if include_expanded and len(sources) > 1 else ""

    # Worktree info
    entry_worktrees = set(e[4] for e in entries if e[4])
    worktree_info = f"wt:{','.join(sorted(entry_worktrees))}" if show_worktree else ""

    info_parts = []
    if total_entries > shown:
        info_parts.append(f"{shown}/{total_entries} ({coverage_pct:.0f}%)")
    if session_info:
        info_parts.append(session_info)
    if source_info:
        info_parts.append(source_info)
    if worktree_info:
        info_parts.append(worktree_info)
    if info_parts:
        print(f"[i] {' '.join(info_parts)}")

    # Output entries (newest first)
    for ts, role, text, source, worktree in reversed(entries):
        text = text.replace('\n', ' ').replace('\r', '')
        if source == "main":
            # Show worktree for main entries when multiple worktrees exist
            prefix = f"[{role}:{worktree}]" if show_worktree and worktree else f"[{role}]"
        else:
            # For agent/tool, show source type
            prefix = f"[{role}:{source[0]}]"
        print(f"{prefix} {text}")

if __name__ == "__main__":
    main()
