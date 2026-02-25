# tabtabtabTABtab

close the browser.

## Install

```
/plugin marketplace add akegaviar/tabtabtabTABtab
```

Then install individual skills:

```
/plugin install spice-must-flow@tabtabtabTABtab
```

## Skills

| Skill | Description |
|-------|-------------|
| **spice-must-flow** | Flow state companion — watches your session and provides reflective insights on demand |
| **frontend-slides** | Create stunning, zero-dependency HTML presentations from scratch or from PowerPoint |

## For skill authors

tabtabtabTABtab curates skills from the community. If your skill is featured here, you'll find:

- **Credit** in the marketplace catalog with your name and repo linked
- **A promo slot** — a link displayed to every user who runs your skill. You control what it points to (your repo, your site, a project). Submit changes via PR to `promos/promos.json`

### How skills are included

Claude Code plugins require skills at `skills/<name>/SKILL.md` relative to the plugin root. If your repo already follows this structure, tabtabtabTABtab references it directly via GitHub URL. If your SKILL.md is at the repo root (the most common layout), tabtabtabTABtab copies it into the monorepo and restructures it to work as a plugin.

**Want tabtabtabTABtab to reference your repo directly?** Restructure to:

```
your-repo/
└── skills/
    └── your-skill-name/
        └── SKILL.md
```

Open an issue or PR and we'll swap the monorepo copy for a direct reference to your repo.

### Suggest a skill

Know a great skill that should be here? [Open an issue](https://github.com/akegaviar/tabtabtabTABtab/issues) with a link to the repo.

## License

MIT
