# bonbonki

Your favorite tab isn't a browser.

A curated channel of Claude Code skills — useful, experimental, and entertaining.

## Install

```
/plugin marketplace add akegaviar/bonbonki
```

Then install individual skills:

```
/plugin install spice-must-flow@bonbonki
```

## Skills

| Skill | Description |
|-------|-------------|
| **spice-must-flow** | Flow state companion — watches your session and provides reflective insights on demand |
| **frontend-slides** | Create stunning, zero-dependency HTML presentations from scratch or from PowerPoint |

## For skill authors

Bonbonki curates skills from the community. If your skill is featured here, you'll find:

- **Credit** in the marketplace catalog with your name and repo linked
- **A promo slot** — a link displayed to every user who runs your skill. You control what it points to (your repo, your site, a project). Submit changes via PR to `promos/promos.json`

### How skills are included

Claude Code plugins require skills at `skills/<name>/SKILL.md` relative to the plugin root. If your repo already follows this structure, bonbonki references it directly via GitHub URL. If your SKILL.md is at the repo root (the most common layout), bonbonki copies it into the monorepo and restructures it to work as a plugin.

**Want bonbonki to reference your repo directly?** Restructure to:

```
your-repo/
└── skills/
    └── your-skill-name/
        └── SKILL.md
```

Open an issue or PR and we'll swap the monorepo copy for a direct reference to your repo.

### Suggest a skill

Know a great skill that should be here? [Open an issue](https://github.com/akegaviar/bonbonki/issues) with a link to the repo.

## License

MIT
