# spice-must-flow

༼🌀🌀༽

Agentic coding is TikTok for builders — unless you protect your flow.

## The problem

Generative work is where flow lives. Generative AI — with *generative* right there in the name — took that from you. Now you prompt, wait, evaluate, prompt, wait, evaluate. So you drift. You open a browser. You check Twitter. You watch a YouTube short.

The drift is your lifetime. It's never coming back.

There are currently two main responses:

1. **Scale it** — run 5 agents in parallel. You sacrifice flow for throughput. Works for execution tasks.
2. **Get mined** — social media's attention playbook, now inside your IDE. Pure extraction.

spice-must-flow is option 3: **protect it.**

## Two tabs

```
TAB 1 — WORK                    TAB 2 — COMPANION
You prompt                       Read-only — can't break anything
You manage context               Single-character input
Agent writes code                Fast — cheap model, small prompt
You evaluate output              In context — reads your session live
You decide what's next

Full cognitive load              Near-zero cognitive load
```

Your main session runs in tab 1. The companion runs in tab 2. When your agent is thinking, Alt+Tab over, type `.` or `..x`, get a reflection, Alt+Tab back.

## Three principles

**1. Stay in the task context.** Don't leave the terminal. Don't open a browser. Don't break the loop. The perspective comes to you — where you already are. `preprocessor.py` reads your sessions live from `~/.claude/projects/`.

**2. Observe, don't act.** The moment something offers to act, you have to evaluate whether to let it. That's cognitive load. A read-only observer creates zero decisions. The skill definition itself forbids changes — `allowed-tools: Bash, Read, Grep, Glob` — no Edit, no Write.

**3. The cost of asking must be near zero.** "What should I ask? How should I phrase it?" — that's already evaluative, that already breaks flow. So you type a single character. `.` for what now. `..` for blind spots. `x` for what breaks. No prompt to craft.

## Quick start

```bash
alias spice="claude --dangerously-skip-permissions --model haiku --strict-mcp-config --no-chrome /spice-must-flow"
```

Then: `spice`

Runs on Haiku with no MCPs, no Chrome UI, permissions skipped. Fast and cheap as a side-channel observer.

## Buttons

Single-character inputs, freely combinable.

```
PERSPECTIVE           ANALYSIS              NAVIGATION
  .   what now?         x   what breaks?      <   rewind 10m
  ..  blind spots?      -   different way?     >   forward
  ... big picture       #   seen before?       p   plan compass
                        ~   gain or drain?

INTERACTION           BONUS
  q   interview         t       timeline today (t+ = all time)
                        harness deep session review ⚙ Opus
                        r       random button

MODIFIERS
  ,   depth (100/200/300/all)
  ^   expanded (include subagent + tool results)
  w   worktrees (all git worktree sessions)
```

Combine freely: `..x,,` = blind spots + breaks (200 entries). `..p` = blind spots + plan alignment. `tw` = timeline across worktrees. Order doesn't matter.

## Architecture

```
Tab 1 (main — Opus)              Tab 2 (companion — Haiku)
     │                                │
     │ writes to                      │ reads
     ▼                                ▼
session1.jsonl ──────────────►  ┌─────────────┐
session2.jsonl ──────────────►  │preprocessor │
session3.jsonl ──────────────►  │ (unified    │
     ⋮                          │  timeline)  │
                                └─────────────┘
                                      │
                                      ▼
                                button response
```

The companion reads Claude Code's session transcripts (JSONL files in `~/.claude/projects/`) and processes them through a Python preprocessor to build a unified timeline of your work. The preprocessor parses your input, counts dots and commas, discovers sessions, filters out companion sessions (to avoid self-referential loops), and outputs a structured transcript with `[buttons: ...]` so the model knows what to respond with.

### Data flow

```
Type buttons → SKILL.md runs preprocessor.py → merges sessions from
~/.claude/projects/ → outputs [buttons: ..x] [i] 30/150 → Haiku responds
```

### Timeline (`t`)

Pure Python, no LLM. Visualizes user vs Claude activity as ASCII art:

```
t | 2h45m | 1h20m Claude | 3 sessions

09:12-10:38 | 86m | 12 exchanges | Claude 55%
░░░░████████░░██████████████░░░██████░░████████████░░░░
██████████░░░████████

░ = you    █ = Claude
```

Width proportional to duration. `t` for today, `t+` for all project history.

### Harness (`harness`)

Bypasses Haiku entirely. `harness.py` assembles the full session transcript and a capabilities reference, then spawns an Opus subagent via the Task tool for deep meta-analysis. Looks for missed parallelism, subagent opportunities, tool choices, context pressure. Haiku runs cheap day-to-day. Opus comes in for the post-mortem.

## Design principles

1. **Unified timeline** — all sessions merged chronologically
2. **Combinable** — mix buttons freely, order doesn't matter
3. **Adaptive scanning** — reads only what's needed, stops at entry limit
4. **Fast TTFT** — minimal skill file, external preprocessor
5. **Read-only** — never modifies files
6. **Model-agnostic** — works on Haiku, Sonnet, Opus

## Files

```
SKILL.md                168 lines — skill definition, behavior rules, button specs
scripts/
  preprocessor.py       382 lines — transcript parser, session merger, button router
  timeline.py           503 lines — ASCII timeline visualization
  harness.py            278 lines — transcript gatherer + Opus analysis prompt builder
```

## License

MIT
