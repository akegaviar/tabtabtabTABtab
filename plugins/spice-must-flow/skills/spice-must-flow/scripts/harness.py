#!/usr/bin/env python3
"""harness — gathers session transcript and builds an analysis prompt for Opus.

Does NOT call any API. Prints the assembled prompt to stdout for the companion
to feed into a Task agent (model: opus, subagent_type: general-purpose).

Usage:
    python3 harness.py "harness"   → today's sessions only
    python3 harness.py "harness+"  → all project history
"""
import json
import os
import re
import sys
from datetime import datetime, timezone
from pathlib import Path


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
    """Check if session is a companion by looking for the actual welcome message."""
    try:
        with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
            content = f.read(8000)
            return '༼🌀🌀༽ Spice flow connected.' in content
    except:
        return False


def get_session_base_paths():
    """Get session directory for current project (no worktree support)."""
    home = Path.home()
    cwd = os.getcwd()
    session_dir = str(home / ".claude/projects" / cwd.replace("/", "-"))
    if os.path.isdir(session_dir):
        return {session_dir: os.path.basename(cwd)}
    return {}


def parse_ts(ts):
    if not ts:
        return None
    try:
        return datetime.fromisoformat(ts.replace("Z", "+00:00"))
    except:
        return None


def extract_entries(filepath):
    """Extract full content entries: User messages, Assistant text, Tool calls + results."""
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
                        c = e.get("message", {}).get("content", "")
                        if isinstance(c, str) and c.strip():
                            if "<command-name>" not in c[:50]:
                                entries.append((ts, "User", c))
                        elif isinstance(c, list):
                            for item in c:
                                if item.get("type") == "text":
                                    entries.append((ts, "User", item.get("text", "")))
                                elif item.get("type") == "tool_result":
                                    content = item.get("content", "")
                                    if isinstance(content, list):
                                        content = " ".join(
                                            block.get("text", str(block)) if isinstance(block, dict) else str(block)
                                            for block in content
                                        )
                                    entries.append((ts, "ToolResult", content))
                    elif t == "assistant":
                        for b in e.get("message", {}).get("content", []) or []:
                            if b.get("type") == "text":
                                entries.append((ts, "Assistant", b.get("text", "")))
                            elif b.get("type") == "tool_use":
                                n = b.get("name", "")
                                inp = b.get("input", {})
                                entries.append((ts, "Tool", f"{n}: {json.dumps(inp, ensure_ascii=False)}"))
                except:
                    pass
    except:
        pass
    return entries


CAPABILITIES_REFERENCE = """## Claude Code Capabilities Reference

- **Parallel tool calls**: Multiple independent tool calls in a single response for speed
- **Task tool with subagents**: Spawn specialized agents (general-purpose, Explore, Plan, Bash, etc.) for parallel or deep work
- **Teams**: Coordinate multiple agents working on a project with shared task lists
- **MCP servers**: External integrations via Model Context Protocol
- **Hooks**: Automation triggered on tool events (pre/post tool execution)
- **CLAUDE.md / project instructions**: Persistent project context and conventions
- **Plan mode**: Design-before-implementation with user approval workflow
- **Worktrees**: Isolated git worktrees for parallel development
- **Skills / slash commands**: Reusable skill definitions invoked via /command
- **Tool choices**: Glob (not find), Grep (not grep), Read (not cat), Edit (not sed) — dedicated tools over shell equivalents
- **Model selection**: Different models for different tasks (Opus for depth, Haiku for speed)
- **Effort levels**: Adjustable reasoning effort per task
- **EnterPlanMode**: Proactively plan before non-trivial implementation
- **Background tasks**: Run long operations in background, check results later
- **Isolation via worktree param on Task tool**: Subagents can work in isolated repo copies
"""

ANALYSIS_INSTRUCTION = """## Your Task

Review this Claude Code session transcript. You are analyzing how an AI coding agent (Claude Code) was used — not the code itself, but the *process* and *agentic patterns*.

Identify specific moments where the work could have been done more effectively using Claude Code's agentic capabilities. Think deeply about this. Be concrete — reference actual parts of the transcript.

Focus on what would have made the biggest difference:
- Were there opportunities for parallelism that were missed?
- Could subagents have been used to explore or research while the main thread continued?
- Were there moments where plan mode would have prevented wasted iterations?
- Did the session use shell commands where dedicated tools would have been better?
- Were there sequential operations that could have been concurrent?
- Could teams or background tasks have accelerated the workflow?
- Were there signs of context window pressure that better delegation could have avoided?
- Did the session miss opportunities to use project instructions (CLAUDE.md) for recurring patterns?

Don't force categories. Some sessions are well-optimized — say so if that's the case. Focus on the insights that actually matter for this specific session.

Be direct and specific. No filler, no generic advice. Reference the transcript.
"""


def main():
    if len(sys.argv) < 2:
        print("[!] Usage: harness.py 'harness' or 'harness+'", file=sys.stderr)
        sys.exit(1)

    user_input = sys.argv[1].strip()
    all_time = '+' in user_input

    base_paths = get_session_base_paths()
    if not base_paths:
        print("[!] No project sessions found", file=sys.stderr)
        sys.exit(1)

    # Find session files
    uuid_pattern = re.compile(r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}\.jsonl$')
    session_files = []
    index_timestamps = {}

    for base_path in base_paths:
        index_timestamps.update(load_index_timestamps(base_path))
        try:
            for f in os.listdir(base_path):
                if uuid_pattern.match(f):
                    session_files.append(os.path.join(base_path, f))
        except OSError:
            continue

    # Sort by recency
    def get_content_timestamp(filepath):
        session_id = os.path.basename(filepath).replace('.jsonl', '')
        if session_id in index_timestamps:
            return index_timestamps[session_id]
        return get_last_content_timestamp(filepath)

    session_files.sort(key=get_content_timestamp, reverse=True)

    # Filter: skip companion sessions, optionally filter to today
    today = datetime.now().date()
    all_entries = []
    sessions_used = 0

    for session_file in session_files:
        if is_companion_session(session_file):
            continue

        entries = extract_entries(session_file)
        if not entries:
            continue

        # Filter to today if not all_time
        if not all_time:
            entries = [
                (ts, role, text) for ts, role, text in entries
                if parse_ts(ts) and parse_ts(ts).astimezone().date() == today
            ]
            if not entries:
                continue

        all_entries.extend(entries)
        sessions_used += 1

    if not all_entries:
        scope = "all time" if all_time else "today"
        print(f"[!] No session entries found for {scope}", file=sys.stderr)
        sys.exit(1)

    # Sort chronologically
    all_entries.sort(key=lambda x: x[0])

    # Format transcript
    transcript_lines = []
    for ts, role, text in all_entries:
        dt = parse_ts(ts)
        time_str = dt.astimezone().strftime("%H:%M:%S") if dt else "??:??:??"
        # Truncate very long entries (tool results can be huge)
        if len(text) > 2000:
            text = text[:2000] + "... [truncated]"
        transcript_lines.append(f"[{time_str}] [{role}] {text}")

    transcript = "\n".join(transcript_lines)
    scope_label = "all project history" if all_time else "today's sessions"

    # Assemble prompt
    prompt = f"""# Harness: Deep Session Analysis

Analyzing {sessions_used} session(s) — {scope_label} — {len(all_entries)} entries.

{CAPABILITIES_REFERENCE}

{ANALYSIS_INSTRUCTION}

## Session Transcript

{transcript}
"""

    print(prompt)


if __name__ == "__main__":
    main()
