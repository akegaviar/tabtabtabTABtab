# spice-must-flow

༼🌀🌀༽

A read-only flow state companion for Claude Code. Observes your active coding session and provides perspective, analysis, and navigation — without interfering.

**How to use it:** Keep a second terminal tab open in the same project directory with spice running. When your main Claude Code is thinking, Alt+Tab over, type `.` or `..x`, get a reflection, Alt+Tab back. Set up a shell alias so launching it is one word:

```bash
alias spice="claude --dangerously-skip-permissions --model haiku --strict-mcp-config --no-chrome /spice-must-flow"
```

## The problem

Agentic coding fractured your workday. You used to write code in one continuous stream. Now you prompt, wait, evaluate, prompt, wait, evaluate. The generative work — where flow lives — got displaced by an AI with "generative" in the name.

So you drift. You open a browser. You check Twitter. You watch a YouTube short. The drift is your lifetime — it's never coming back. And your ability to focus erodes with every context switch.

There are currently two main responses:

1. **Scale it** — run 5 agents in parallel. You sacrifice flow for throughput. Works for execution tasks.
2. **Let someone mine it** — social media's attention playbook, now inside your IDE. Pure extraction.

spice-must-flow is option 3: **protect it.**

## Three principles

The companion implements three metacognition principles that keep you in flow during agent wait time:

**1. Stay in the task context.** Don't leave the terminal. Don't open a browser. Don't break the loop. The perspective comes to you — where you already are. `preprocessor.py` reads your sessions live from `~/.claude/projects/`.

**2. Observe, don't act.** The moment something offers to act, you have to evaluate whether to let it. That's cognitive load. A read-only observer creates zero decisions. The skill definition itself forbids changes — `allowed-tools: Bash, Read, Grep, Glob` — no Edit, no Write.

**3. The cost of asking must be near zero.** "What should I ask? How should I phrase it?" — that's already evaluative, that already breaks flow. So you type a single character. `.` for what now. `..` for blind spots. `x` for what breaks. No prompt to craft.

## Quick start

Open a second terminal in the same project directory:

```bash
claude --dangerously-skip-permissions --model haiku \
       --strict-mcp-config --no-chrome "/spice-must-flow"
```

Or set up an alias:

```bash
alias spice="claude --dangerously-skip-permissions --model haiku --strict-mcp-config --no-chrome /spice-must-flow"
```

Then: `spice`

Runs on Haiku with no MCPs, no Chrome UI, permissions skipped, thinking off. Fast and cheap as a side-channel observer.

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

## How it was built

spice-must-flow was developed across 25+ handoff sessions over 6 weeks, starting January 2026. Each session picked up from a structured handoff document — task status, learnings, artifacts, action items — and pushed the skill forward through iterative development with Claude Code itself.

### Key learnings from development

**Haiku garbles formatted output.** When the skill said "output this text", Haiku would interpret and reformat instead of copying verbatim. Solution: move all formatting to Python scripts, keep SKILL.md minimal, use example-based response formats.

**Prompt length directly impacts TTFT.** Externalizing the preprocessor from the skill file (463 → 60 lines) dramatically reduced the "Puzzling..." delay before the first Bash call. The skill became a thin dispatcher; Python does the work.

**Text clipping was premature optimization.** Original 1000-char truncation caused mid-sentence cuts. For Haiku on Claude Max, the 200k context window and cost are non-issues. Better to limit entry count and let the model see full content.

**Input parsing belongs in the script, not the model.** Counting dots, commas, detecting button combos — Claude was unreliable at this. Moving parsing to Python and outputting `[buttons: ...]` made it deterministic.

**Companion sessions must self-filter.** Without detection markers (`༼🌀🌀༽` + `SPICE_10191`), the companion would read its own transcripts and loop. Filtering reads 8000 bytes from each session to find the marker.

**Read-only enforcement needs teeth.** Haiku tried to edit files when asked `>` (interpreted as "implement next step"). Fixed by strengthening the read-only section with explicit "NEVER" rules and removing Edit/Write from allowed tools.

### Design principles

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
