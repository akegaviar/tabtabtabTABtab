# tabtabtabTABtab

> burn tokens for emergence

An experimental SKILL marketplace for Claude Code. Your agents run in tabs, turning browser-detour downtime into token-burn experiments where things emerge. [Why?](#the-thesis)

This is where I ship SKILLs. [Discussions](https://github.com/akegaviar/tabtabtabTABtab/discussions) and [issues](https://github.com/akegaviar/tabtabtabTABtab/issues) are open. Come say hi.

## Install

```
/plugin marketplace add akegaviar/tabtabtabTABtab
```

Each skill has its own README — browse the directories above.

> After installing, enable auto-updates: `/plugin marketplace auto-update akegaviar/tabtabtabTABtab`

## The thesis

SKILLs are a new form factor affecting both how they're produced and how they're consumed. A human alone won't consume and run a SKILL. An agent alone has no reason to consume and run a SKILL. SKILLs are consumed by the pair — what I call a **dyad**.

### SKILL types

There are three SKILL types per Anthropic:

**Domain expertise.** The SKILL author's specialized knowledge, encoded. The consumer can use someone else's SKILL but can't make a judgement on it as they lack the domain knowledge to evaluate quality. Trust in the author is load-bearing.

Example: Anthropic's official skill-creator SKILL. It encodes Anthropic's domain expertise about what makes a good SKILL. The consumer gets better SKILLs but can't evaluate whether the conventions are the right ones — they're trusting Anthropic's accumulated knowledge about their own system.

**Repeatable workflow.** A process, automated and packaged. The result is verifiable, which is why coding agents have been the first to take off.

Example: The chans SKILL in this repository. The execution is verifiable.

**New capability.** Something the LLM powering the agent can't do well on its own or can't do at all, but a properly harnessed agent can. A capability uplift.

Example: The markdown-tables SKILL in this repository. The LLM produces bad markdown tables natively; with a SKILL, it produces good ones.

### Emergence

When composed, SKILLs produce emergent things — a new SKILL that none of the parts could be alone.

Any combination of any SKILL types works towards emergence:
* 1 domain SKILL + 1 workflow SKILL + 1 capability SKILL = 1 emergent SKILL
* 2 workflow SKILLs + 1 capability SKILL = 1 emergent SKILL
* 1 domain SKILL + 1 domain SKILL = 1 emergent SKILL
* etc

Emergence, of course, works on all levels of life and operation -- within our context:
* 1 human + 1 agent = 1 dyad (emergent entity)
* 1 dyad + 1 dyad = 1 emergent entity
* 1 dyad + 2 agents = 1 emergent entity
* etc

### Marketplace

This marketplace is a combinatorial space and an experimental exhibition for dyads.

Dyads (especially Claude Code dyads) have idle time — forced breaks waiting for long runs, voluntary breaks between tasks. That attention currently leaks to browsers, YouTube, X. tabtabtabTABtab captures this attention inside the tool to burn tokens for experimental emergence.

### Dyad primitives

Four concepts, each building on the last.

**Dyad > Harnessing > SKILL > Marketplace**

A dyad operates. Through operating, harnessing accumulates. Through harnessing, SKILLs of three types (domain, workflow, capability) precipitate. Through SKILLs, a marketplace becomes possible. Each stage is a product of the one before it — you can't skip steps. A SKILL that wasn't born from real dyad iterations is just a prompt template. A marketplace of such SKILLs is just a prompt library.

**Dyad.** A human-agent pair operating as a single cognitive unit. Not a person using an assistant — a fused entity where neither half can replicate the other's contribution. Domain expertise is the amplifier: a human operating within their area of expertise makes the dyad disproportionately more productive. Outside their niche, the human becomes noise.

**Harnessing.** The process by which a dyad gets stronger through use. Two reinforcing loops: the human learns the model (how it reasons, where it drifts, what produces reliable results) and the human builds orchestrations (SKILLs, hooks, workflows) that encode that knowledge. Deeper model knowledge enables better orchestrations. Better orchestrations deepen model knowledge.

**SKILL.** The codified, portable output of harnessing. A distillation, not a recording — it captures what the dyad *learned* through doing, not what it did. A SKILL encodes two kinds of knowledge at once: domain expertise (how to do the task) and model expertise (how to work with this agent). Many iterations produce one SKILL. The harnessing has to happen first.

**Marketplace.** Where SKILLs from one dyad become available to others. A SKILL transfers capability, not judgment — the consuming dyad integrates it into their own domain work, where their own expertise is still load-bearing. The marketplace is what happens when a dyad's private advantage becomes shared infrastructure.

## License

MIT
