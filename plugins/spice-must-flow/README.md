# spice-must-flow

A read-only flow state companion for Claude Code. Observes your active coding session and provides perspective, analysis, and navigation — without interfering.

## Launch

```bash
cld -s            # launches via: claude --dangerously-skip-permissions --model haiku \
                  #   --strict-mcp-config --mcp-config empty.json --no-chrome "/spice-must-flow"
                  # thinking disabled automatically (MAX_THINKING_TOKENS=0)
```

Runs on Haiku with no MCPs, no Chrome UI, permissions skipped, and thinking off. This keeps it fast and cheap as a side-channel observer.

## How it works

The companion reads your Claude Code session transcripts (JSONL files in `~/.claude/projects/`) and responds to button-combo inputs.

Three Python scripts do the heavy lifting:

- **preprocessor.py** — Parses session transcripts, extracts recent entries, detects plans, and routes button combos to the right analysis
- **timeline.py** — Generates ASCII timeline visualizations showing User vs Claude activity over time
- **harness.py** — Gathers transcript and builds a deep analysis prompt; fed into an Opus subagent via the Task tool for meta-analysis of agentic patterns

## Buttons

```
PERSPECTIVE           ANALYSIS              NAVIGATION
  .   what now?         x   what breaks?      <   rewind 10m
  ..  blind spots?      -   different way?     >   forward
  ... big picture       #   seen before?       p   plan compass
                        ~   gain or drain?

INTERACTION           BONUS
  q   interview         t       timeline today
                        t+      all-time timeline
                        harness deep session review ⚙ Opus
                        harness+ all-time review ⚙ Opus

MODIFIERS
  ,   depth (100/200/300/all)
  ^   expanded (include subagent + tool results)
  w   worktrees (all git worktrees, not just current dir)
```

Buttons are combinable: `..x,,` = blind spots + breaks (200 entries), `tw` = timeline across worktrees.

## Files

```
SKILL.md              Skill definition, behavior rules, button specs
scripts/
  preprocessor.py     Transcript parser and button router
  timeline.py         ASCII timeline visualization
  harness.py          Transcript gatherer + Opus analysis prompt builder
```
