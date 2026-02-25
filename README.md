# tabtabtabTABtab

`kill the browser, burn tokens.`

An experimental skill marketplace for Claude Code. Your agents run in tabs — the TAB is where you go instead of opening a browser.

Flow tools, trading, games, experiments.

## Install

```
/plugin marketplace add akegaviar/tabtabtabTABtab
```

Browse what's available:

```
/plugin install
```

Install a skill:

```
/plugin install spice-must-flow@tabtabtabTABtab
```

## Skills

| Skill | What it does |
|-------|-------------|
| **spice-must-flow** | Flow state companion. Watches your session, provides reflective insights on demand. Single-character inputs — `.` for what now, `..` for blind spots, `x` for what breaks. Runs on Haiku in a second tab. [README →](plugins/spice-must-flow/README.md) |
| **frontend-slides** | Create zero-dependency HTML presentations from scratch or from PowerPoint. Show-don't-tell design discovery. [upstream →](https://github.com/zarazhangrui/frontend-slides) |

## The thesis

Every new form factor — apps, posts, stories — changed what got made and how it got consumed. Skills are the next form. You can't use one without the agent. The human directs, the agent executes, both shape the outcome. This is structurally different from every prior form factor.

A dyad watches a YouTube video differently than a human alone — the agent fetches the transcript, surfaces key points, connects it to context. A dyad reads a paper differently — the agent maps arguments, the human provides judgment. The consumption mode itself is new.

Claude Code dyads have idle time — forced breaks waiting for long runs, voluntary breaks between tasks. That attention currently leaks to browsers, YouTube, X. tabtabtabTABtab captures it inside the tool.

## How skills are built

Every skill is born from real use. [spice-must-flow](plugins/spice-must-flow/README.md) is at v8 — months of daily use, architectural rewrites, model compatibility testing. This is distillation, not prompt templating. The catalog is mostly original work, occasionally a fork improved through the same process.

## License

MIT
