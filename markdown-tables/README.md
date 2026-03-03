# markdown-tables

Models produce valid markdown tables. They render fine. But open the source and you get this:

```
| Feature | Supported | Description | Notes |
|---|---|---|---|
| WebSocket | Yes | Real-time bidirectional communication protocol for streaming data | Requires v2.0 or later, see migration guide for upgrade path |
| REST | Yes | Standard HTTP request-response API access | Available on all plans |
| GraphQL | Partial | Query language for flexible data fetching | Beta support only, limited to read operations |
```

Correct? Technically. Readable at source? No. The columns collapse, the pipes don't align, status values waste space, and long cells force horizontal scrolling. It renders fine in a browser — but you're not in a browser. You're in VS Code, in a terminal, in a diff view.

This skill makes tables human-readable at source:

```
| Feature   | Support | Notes          |
|-----------|:-------:|----------------|
| WebSocket | ✓¹      | Streaming data |
| REST      | ✓       | All plans      |
| GraphQL   | ○²      | Read-only      |

¹ Requires v2.0+. See migration guide.
² Beta support only.
```

Same information. Aligned columns, symbols instead of text, footnotes instead of sprawl, width-budgeted to fit your editor.

## What it does

- Replaces text statuses (Yes/No/Partial/N/A) with symbols (✓/✗/○/—)
- Aligns columns and pipes for source readability
- Moves long cell content to footnotes — never truncates
- Splits wide tables (9+ columns) into focused sub-tables with shared keys
- Abbreviates headers (not cell content) when tables exceed width budgets
- Adds legends when symbols need explanation
- Fixes broken tables: mismatched column counts, missing delimiters, missing pipes

## Cost

Takes roughly 2x the tokens of a default table — the skill instructions are ~500 lines of rules, examples, and reference files. But it runs in `context: fork`, so none of that touches your main conversation. The forked context loads, does the table work, and returns the result. Your main context stays clean.

## Width budgets

Every table targets a character width based on where it'll be read:

| Target         | Width       |
|----------------|-------------|
| VS Code (default) | 120 chars |
| GitHub         | 110 chars   |
| Terminal       | 80 chars    |
| Wide (docs sites) | 150 chars |

Defaults to 120. The skill applies a compression cascade — symbols, then header abbreviation, then footnotes, then splitting — and stops the moment every row fits.

## Cardinal rule

**Never truncate. Restructure, footnote, split — but never lose content.**

No `...`, no silent column drops, no abbreviated cell values. Every piece of information survives. If a cell is too wide, the full content moves to a footnote. If there are too many columns, the table splits. Structure bends; content doesn't.

## Files

```
SKILL.md                 513 lines — rules, workflow, compression cascade, anti-patterns
references/
  before-after-examples.md   228 lines — 6 complete transformations with techniques annotated
  symbol-reference.md              — full Unicode symbol table, cross-platform compatibility
  width-budget-cheatsheet.md       — platform measurements, VS Code font metrics
```

## License

MIT
