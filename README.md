# tabtabtabTABtab

> kill the browser, burn tokens.

An experimental skill marketplace for Claude Code. Your agents run in tabs — the TAB is where you go instead of opening a browser.

Flow tools, trading, games, experiments. [Why?](#the-thesis)

## Install

```
/plugin marketplace add akegaviar/tabtabtabTABtab
```

## Skills

| Skill | What it does |
|-------|-------------|
| **spice-must-flow** | Read-only session companion. Your agent is thinking — Alt+Tab over, type `.`, get a reflection, Alt+Tab back. [README](plugins/spice-must-flow/README.md) |

## The thesis

Skills are a new form factor. Every new form factor — apps, posts, stories — changed what got made and how it got consumed. Skills are the next form. A human alone can't run one. An agent alone won't. They're consumed by the pair — what we call a **dyad**.

A dyad watches a YouTube video differently than a human alone — the agent fetches the transcript, surfaces key points, connects it to context. A dyad reads a paper differently — the agent maps arguments, the human provides judgment. The consumption mode itself is new.

Claude Code dyads have idle time — forced breaks waiting for long runs, voluntary breaks between tasks. That attention currently leaks to browsers, YouTube, X. tabtabtabTABtab captures it inside the tool.

### Dyad primitives

Four concepts, each building on the last.

**Dyad > Harnessing > Skill > Marketplace**

A dyad operates. Through operating, harnessing accumulates. Through harnessing, skills precipitate. Through skills, a marketplace becomes possible. Each stage is a product of the one before it — you can't skip steps. A skill that wasn't born from real dyad iterations is just a prompt template. A marketplace of such skills is just a prompt library.

**Dyad.** A human-agent pair operating as a single cognitive unit. Not a person using an assistant — a fused entity where neither half can replicate the other's contribution. Domain expertise is the amplifier: a human operating within their area of expertise makes the dyad disproportionately more productive. Outside their niche, the human becomes noise.

**Harnessing.** The process by which a dyad gets stronger through use. Two reinforcing loops: the human learns the model (how it reasons, where it drifts, what produces reliable results) and the human builds orchestrations (skills, hooks, workflows) that encode that knowledge. Deeper model knowledge enables better orchestrations. Better orchestrations deepen model knowledge.

**Skill.** The codified, portable output of harnessing. A distillation, not a recording — it captures what the dyad *learned* through doing, not what it did. A skill encodes two kinds of knowledge at once: domain expertise (how to do the task) and model expertise (how to work with this agent). Many iterations produce one skill. The harnessing has to happen first.

**Marketplace.** Where skills from one dyad become available to others. A skill transfers capability, not judgment — the consuming dyad integrates it into their own domain work, where their own expertise is still load-bearing. The marketplace is what happens when a dyad's private advantage becomes shared infrastructure.

## License

MIT
