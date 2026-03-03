---
name: markdown-tables
description: Fix, create, or reformat markdown tables. MUST load before editing any markdown table. Use when fixing tables, reformatting wide or broken tables, creating new tables, aligning columns, choosing table structure, compressing table width, or generating any tabular markdown. Contains required width budgets, symbol conventions, and compression rules. Do NOT use for CSV files, spreadsheets, JSON-to-table conversion, or HTML table generation.
context: fork
---

# Markdown Table Design

## Cardinal Rule

**Never truncate. Restructure, footnote, split — but never lose content.**

Every piece of information must survive transformation. If a table is too wide, compress it.
If compression isn't enough, split it. If splitting loses relationships, use footnotes and legends.
Never use `...`, never silently drop columns, never abbreviate to the point of ambiguity.

**Compression applies to structure, not content.** You may shorten column headers, replace
status text with symbols (Yes/No → ✓/✗), and restructure the table layout. Symbol replacement
is not abbreviation — it's lossless semantic compression where the meaning is preserved exactly.
You must NOT truncate or abbreviate cell data — every column's values are content that readers
depend on. If cell content is too wide, move it to a footnote; don't shorten it.

**Every cell is content.** This applies to all columns — not just the "key" column. Names,
descriptions, notes, identifiers, qualifiers, categories — if a human wrote it in a cell,
it's content. The only things eligible for shortening are column headers (and replacing
status text with equivalent symbols).

**Assess before editing.** Read the entire file first. Tables may already use symbols, have
legends, use footnotes, or fit the width budget — don't assume they need transformation.
Check each table's actual state before changing it. If a table is already correct, leave it
alone. Edit tables directly using your text editing tools — never write Python, JavaScript,
or shell scripts for batch transformation. Scripts can't adapt to per-table context and
risk undoing existing footnotes, expanding legends, or violating the rules above.

---

## Workflow

Follow these steps in order for every table task.

### Step 1: Assess

Read the entire file. For each table, note:
- Current width (count the longest row in chars)
- Column count
- Whether symbols, legends, or footnotes are already in use
- Whether any column has the same value in every row (uniform column — candidate for removal)
- Whether the table is syntactically valid (equal column counts across all rows, leading/trailing pipes, blank lines before and after)

If a table is already correct and within budget, leave it alone.

### Step 2: Diagnose Problems

Check for issues from the error recovery list below:
- Mismatched column counts between rows
- Missing delimiter row
- Missing leading/trailing pipes
- Missing blank lines before/after the table
- HTML tags that won't render in the target environment
- Cells containing unescaped `|` characters

Fix syntax problems before doing any structural work.

### Step 3: Decide Structure

Use the Decision Framework below to determine:
- Is a table the right format? (1-3 columns → consider a list instead)
- Standard, comparison, transposed, or split?
- What alignment per column?

### Step 4: Transform

If the table exceeds the width budget, apply the Priority Cascade — symbols first, then headers, then footnotes, then legend, then merge, then split. Stop as soon as every row fits.

Use the Symbols and Compression Techniques sections as reference during this step.

### Step 5: Verify

After every transformation, check:
- [ ] Every row is under the width budget
- [ ] Column count is identical in header, delimiter, and all data rows
- [ ] No content was lost — every original cell value is either in the table or in a footnote
- [ ] Footnotes are numbered sequentially and all referenced markers exist
- [ ] Legend covers all symbols used (if applicable)
- [ ] Blank line before and after every table
- [ ] Pipes are vertically aligned (preferred, not required)
- [ ] Existing footnotes and legends from the original were preserved

If verification fails, go back to Step 4. Do not add new problems while fixing others.

---

## Error Recovery

Handle these common malformed-table problems before applying any structural changes.

**Mismatched column counts:**
Count cells in the header row — that's the canonical count. For data rows with too few cells, add empty cells at the end. For rows with too many, check if an unescaped `|` split a cell incorrectly (fix with `\|`), or if two columns were accidentally merged (split them back).

**Missing delimiter row:**
Add a delimiter row (`|---|---|---|`) matching the header's column count. Without it, the table won't render.

**Pasted content with tabs or irregular spacing:**
Normalize to pipe-delimited format. Convert tabs to `|`, ensure consistent column count, add padding spaces.

**HTML tags in cells:**
If the target is VS Code or terminal, replace `<br>` with footnotes or multi-value comma lists. If web-only, HTML is acceptable but note it in a comment.

**Table preceded/followed by text without blank lines:**
Add blank lines. Without them, many parsers merge the table with surrounding text.

---

## Width Budgets

Choose a target width based on where the table will be read:

| Target | Width | Use When |
|--------|-------|----------|
| VS Code default | **120 chars** | Source view on 16" laptop, default font |
| GitHub | **110 chars** | README or repo markdown |
| Universal | **80 chars** | Terminal, email, narrow displays |
| Wide | **150 chars** | Dedicated documentation sites, MkDocs |

**Default to 120 chars** unless the user specifies otherwise.

### Width Arithmetic

```
Total width = sum of column contents + (columns + 1) pipes + (columns × 2) padding spaces

Example: 6 columns, avg 15 chars each
= 90 content + 7 pipes + 12 spaces = 109 chars ✓ (fits 120)
```

### Priority Cascade When Over Budget

When a table exceeds the width budget, apply these techniques in order:

1. Replace text with symbols (Yes/No → ✓/✗)
2. Abbreviate column headers
3. Eliminate uniform columns (every cell has the same value → note below the table)
4. Move details to footnotes below the table
5. Add a legend section for repeated abbreviations
6. Merge related columns (e.g., "First Name" + "Last Name" → "Name")
7. Split into multiple tables with a shared key column

Stop as soon as every row is under budget. Apply the minimum change at each step — if
expanding an abbreviation makes the table wider, compensate with the least disruptive
technique first (reduce column padding, then abbreviate a header by a few chars) before
resorting to footnotes. Once under budget, stop editing — don't keep shaving characters.

---

## Decision Framework

### Step 1: Count Columns

| Columns | Action |
|---------|--------|
| 1-3 | Consider if a table is even needed; a list may be clearer |
| 4-5 | Ideal range. Proceed normally |
| 6-7 | Fine if cells are short (symbols, short text). Watch total width |
| 8 | Look for columns to merge or move to footnotes |
| 9+ | **Must split** into multiple tables or transpose |

### Step 2: Estimate Width

Quick estimate: count the widest expected value in each column, add pipes and padding.

```
Widest values: 20 + 8 + 5 + 5 + 5 + 12 = 55 content
Overhead: 7 pipes + 12 padding = 19
Total: 74 chars ✓
```

### Step 3: Choose Structure

- **Standard table**: 4-7 columns, mixed content types
- **Comparison table**: Features as rows, options as columns. Use symbols for status
- **Transposed table**: When you have 2-3 items but many attributes, flip rows/columns
- **Split tables**: Share a key column (e.g., "Feature") across two adjacent tables
- **Nested list**: When cells contain paragraphs, abandon tables entirely

### Step 4: Choose Alignment

| Content Type | Alignment | Example |
|-------------|-----------|---------|
| Text, names | Left `:---` | Protocol names, descriptions |
| Status, symbols | Center `:---:` | ✓, ✗, —, status badges |
| Numbers | Right `---:` | Prices, counts, percentages |
| Mixed | Left `:---` | Default when unsure |

---

## Symbols

### Default Symbol Set (Cross-Platform Safe)

Use these by default. They render correctly in VS Code, GitHub, Obsidian, terminals, and most editors:

| Symbol | Meaning | Use For |
|--------|---------|---------|
| ✓ | Yes / Supported / Pass | Positive status |
| ✗ | No / Unsupported / Fail | Negative status |
| — | Not applicable / N/A | Neutral, doesn't apply |
| ○ | Partial / In progress | Intermediate status |
| ● | Full / Complete | Filled counterpart to ○ |

Only use symbols from the Primary set above or the Extended set in
[symbol-reference.md](references/symbol-reference.md). Don't invent custom Unicode symbols
or modifier letters (e.g., ✓ᴱ) — they may not render consistently across platforms. If you
need a qualified symbol like "Enterprise only", use a footnote marker (✓¹) instead.

### When to Use Emoji

Only use emoji (✅❌⚠️) when **all** of these are true:
- Target is web-only (GitHub, docs site)
- User explicitly requests emoji
- No terminal or source-view rendering needed

### Symbols to Avoid

| Avoid | Problem | Use Instead |
|-------|---------|-------------|
| ✔ (U+2714) | Inconsistent rendering | ✓ (U+2713) |
| ✘ (U+2718) | Inconsistent rendering | ✗ (U+2717) |
| - (hyphen) | Confused with list markers | — (em dash) |
| N/A (text) | Wastes 3 chars | — |
| Yes/No (text) | Wastes 2-3 chars per cell | ✓/✗ |

---

## Content Compression Techniques

Apply in this order. Stop when under width budget.

### Replace Text with Symbols

```
BEFORE: | Yes | No  | N/A | Partial |    (19 chars across 4 cells)
AFTER:  | ✓   | ✗   | —   | ○       |    (7 chars across 4 cells)
```

### Abbreviate Headers (Not Cell Content)

Shorten **column headers only**. Use a legend below the table if abbreviations aren't obvious.

```
BEFORE: | Protocol | Supported Methods | Rate Limit | Authentication |
AFTER:  | Protocol | Methods           | Rate       | Auth           |
```

Rules for header abbreviation:
- Keep at least 4 chars for recognizability
- Never abbreviate the key column (usually column 1)
- Put units in headers, not cells: `Latency (ms)` instead of repeating "ms" in every row
- Common safe abbreviations: Auth, Config, Desc, Doc, Env, Impl, Info, Max, Min, Msg, Num, Req, Resp, Src, Spec, Val

**Cell content is NOT eligible for abbreviation.** Any shortening of any word in a cell
is abbreviation. This means every column, not just the key column. Do not:
- Drop words from names or labels: "Acute care facility" → "Acute care" loses meaning
- Shorten paths, identifiers, or references: exact values must stay exact
- Compress notes into fragments: "Requires admin approval" → "admin req" is lossy
- Abbreviate proper nouns or product names: "PostgreSQL" must stay, not become "Postgres"
- Shorten any common word: options→opts, details→det., configuration→config, dedicated→ded.,
  description→desc, Enterprise→Ent., Security→Sec., authentication→auth — if the word got
  shorter, it's abbreviation, even if the short form feels "obvious"

**Exception — standardized codes.** Widely-recognized standard codes that readers already
know are not lossy abbreviation: ISO country codes (US, UK, JP), state/province codes
(CA, NY, QLD), stock tickers (AAPL, MSFT), medical codes (ICD-10, CPT), currency codes
(USD, EUR), HTTP methods (GET, POST). These may stay in cells as-is. When using domain
codes that may not be obvious to all readers, add a legend below the table.

If a cell's value is different from another cell's value in the same column, that difference
is information. Don't replace distinct values with the same symbol — e.g., if rows contain
GET, POST, PATCH, DELETE, don't collapse them all to ✓. The reader needs to know *which*
operation, not just that one exists.

If a cell's content makes the table too wide, move the **full, unmodified** content to a
footnote below the table. The cell gets a footnote marker (✓¹) and the detail lives outside
the table at its original length. Do not create an intermediate shortened version — go
straight from the original cell content to a footnote marker. Never abbreviate a cell AND
add a footnote for the full form (e.g., "v1 config ¹" with "¹ v1 configuration parameter"
is wrong — either keep "v1 configuration" in the cell or replace it entirely with a marker).

### Eliminate Uniform Columns

If every cell in a column has the same value, the column adds no comparative information —
it's constant data, not tabular data. Remove the column and state the value as a note below
the table.

```
BEFORE: | Endpoint   | Method | Path       | Resp |    ← "Resp" is "JSON" in every row
AFTER:  | Endpoint   | Method | Path       |

All endpoints return JSON responses.
```

This is free width savings with zero information loss. Check for uniform columns during
assessment (Step 1) before applying heavier techniques like footnotes or splitting.

### Move Details to Footnotes

Use Unicode superscript numbers (¹²³⁴⁵⁶⁷⁸⁹) in cells, with a notes section below the table.
If a table already has footnotes, preserve them — never expand footnoted content back inline.

Don't footnote content under ~25 characters. The readability cost of jumping below the table
outweighs a few chars of width savings. Only footnote when the content genuinely won't fit
inline after applying steps 1–3 (symbols, header abbreviation, uniform column removal). If a short note (like
"Jan 2025" or "Name only") already fits inline and the table is under budget with it there,
keep it inline — footnotes are a last resort for width, not a default compression tool.

**Parenthetical qualifiers belong inline, not in footnotes.** When a symbol replaces Yes/No
but the cell had a short qualifier (a product name, instance type, or tier), keep it as a
parenthetical. This is the natural pattern for "yes, specifically this one":

```
BEFORE: | Yes (EKS)              |    AFTER: | ✓ (EKS)              |     ← inline, not footnoted
BEFORE: | $0.0464/hr (t3.medium) |    AFTER: | $0.0464/hr (t3.medium) |   ← qualifier stays
BEFORE: | Yes (RDS, Aurora, DynamoDB) |  →  | ✓ (RDS, Aurora, DynamoDB) |  ← still only 27 chars
```

Only footnote the qualifier when the full cell genuinely exceeds what fits — e.g., a
comma-separated list of 5+ service names or a multi-sentence caveat. Short product names
(EKS, CloudFront, t3.medium, S3) should never become footnotes.

**Watch your footnote count.** If you're generating more than ~8 footnotes for a single table,
step back and reconsider. Excessive footnotes turn a table into a scavenger hunt — the reader
is constantly jumping below the table to decode cells. Most tables should need 0–5 footnotes
for genuine caveats and exceptions. If you're footnoting every cell in a column, the data
probably fits inline (as parenthetical qualifiers) or the table needs a different structure.

```markdown
| Feature | Support |
|---------|---------|
| WebSocket | ✓¹ |
| REST | ✓ |
| GraphQL | ○² |

¹ Requires v2.0+. See [migration guide](link).
² Beta support only. Limited to read operations.
```

Rules:
- Number footnotes sequentially starting from ¹ within each table
- Place footnotes directly below their table, before the next table or heading
- When splitting into sub-tables, restart numbering at ¹ for each sub-table — each
  sub-table is self-contained with its own footnotes immediately below it
- Keep footnote text to one line each
- Use for: version requirements, caveats, links, exceptions
- If footnoting leaves every cell in a column as just a marker (¹, ², ³...), the column has
  degenerated — it's no longer functioning as a table column. Remove the column and attach
  the footnote markers to the key column instead

```
BEFORE: | Name         | Desc |     AFTER: | Name           |
        | List Users   | ¹    |            | List Users ¹   |
        | Create User  | ²    |            | Create User ²  |
```

### Add a Legend

When multiple columns use the same set of symbols or abbreviations:

```markdown
| Chain | WS | REST | Trace | Debug |
|-------|:--:|:----:|:-----:|:-----:|
| Ethereum | ✓ | ✓ | ✓ | ○ |
| Solana | ✓ | ✓ | ✗ | — |

**Legend:** ✓ Supported | ✗ Not supported | ○ Partial | — N/A
```

### Merge Columns

Combine closely related columns:

```
BEFORE: | First Name | Last Name | Email         |
AFTER:  | Name       | Email         |

BEFORE: | Min Instances | Max Instances |
AFTER:  | Instances (min-max)           |
```

### Split Tables

Last resort. Split into two tables sharing a key column:

```markdown
**Protocols: API Support**

| Protocol | REST | WebSocket | GraphQL |
|----------|:----:|:---------:|:-------:|
| Ethereum | ✓    | ✓         | ✗       |
| Solana   | ✓    | ✓         | ✗       |

**Protocols: Debug Features**

| Protocol | Trace | Debug | Archive |
|----------|:-----:|:-----:|:-------:|
| Ethereum | ✓     | ○     | ✓       |
| Solana   | ✗     | —     | ✓       |
```

Rules for splitting:
- Always repeat the key column in every sub-table
- Give each sub-table a descriptive heading
- Keep related columns together in the same sub-table
- Place sub-tables adjacent (no content between them)
- Restart footnote numbering at ¹ for each sub-table — each sub-table is a self-contained
  unit with its own footnotes directly below it, not a continuation of a previous table

---

## Formatting Rules

### Padding

- One space after `|`, one space before `|` in every cell
- Align pipes vertically for source readability (optional but preferred)
- Right-pad cell contents to column width for visual alignment

```markdown
| Short | Medium value | Long column header |
|-------|--------------|-------------------|
| A     | Something    | Data here         |
```

### Empty Cell Semantics

Empty cells, dashes, and symbols mean different things. Be intentional:

| Cell Content | Meaning |
|-------------|---------|
| (empty) | Unknown, not yet evaluated, or data missing |
| — | Not applicable; this row/column combination doesn't apply |
| ✗ | Evaluated and confirmed negative / unsupported |
| TBD | Acknowledged but not yet determined |

### Multi-Value Cells

When a cell needs multiple values:

```markdown
| Protocol | Methods          |
|----------|-----------------|
| Ethereum | REST, WS, IPC   |
| Solana   | REST, WS        |
```

- Use comma-separated values for short lists (2-4 items)
- Use semicolons when items contain commas
- If a cell needs more than 4 values, move to a footnote or separate table

### Syntax Gotchas

- **Blank lines:** Always put a blank line before and after a table. Without one, parsers can misparse or swallow the following paragraph into the table
- **Cell count:** The header row, delimiter row, and every data row must have the same number of `|`-delimited cells or the table won't parse
- **Leading/trailing pipes:** Always include them. They're technically optional in GFM but omitting them causes parser edge-cases and hurts source readability
- **Literal pipes:** Use `\|` inside cells. Unescaped `|` breaks column boundaries
- **Code spans:** Inline backticks work fine (`SELECT *`). Fenced code blocks do not — markdown tables are single-line per row
- **Multiline cells:** Not supported in GFM. If you need multiline content, that's a signal to restructure: move the content to a footnote, a list below the table, or abandon the table for a definition list
- **HTML in cells:** Works on GitHub/Obsidian (`<br>`, `<sub>`) but breaks in terminals and many editors. Avoid unless targeting web renderers exclusively

---

## Before/After Examples

See [before-after-examples.md](references/before-after-examples.md) for 6 complete transformation examples with techniques annotated, including:

- **Symbol compression** — replacing text status values with ✓/✗/○ symbols and footnotes
- **Table splitting** — breaking 9+ column tables into focused sub-tables with shared key columns
- **Header abbreviation** — shortening headers while preserving cell content
- **Footnote extraction** — moving lengthy cell values below the table

---

## Anti-Patterns

Never do these:

| Anti-Pattern | Why It's Wrong | Do Instead |
|-------------|---------------|------------|
| `...` truncation | Loses information | Footnote or legend |
| Abbreviating cell content | Readers depend on exact values | Only abbreviate headers; footnote long cells |
| Common word shortenings | opts, ded., config, Sec., auth are still abbreviation | Keep the full word in the cell |
| Collapsing distinct values to ✓ | Erases what each row actually says | Keep the distinct values; footnote if wide |
| Drop column silently | Information lost | Move to footnote or second table |
| 150+ char rows | Wraps in most editors | Apply compression cascade |
| Inconsistent symbols | ✓ in one table, ✔ in another | Pick one set, use everywhere |
| Empty = No | Ambiguous meaning | Use ✗ for No, empty for unknown |
| Batch script transformation | Rigid logic undoes existing work | Edit each table directly |
| Abbreviate + footnote combo | "v1 config ¹" with "¹ configuration" is double lossy | Keep original or use footnote marker only |
| Footnoting short content | "Jan 2025" or "Name only" doesn't need a footnote | Keep inline if under ~25 chars and table fits |
| Excessive footnotes (10+) | Table becomes a scavenger hunt | Use inline parentheticals for short qualifiers; restructure if needed |
| Expanding footnotes inline | Widens table, loses structure | Preserve existing footnotes |
| Editing past the budget | Introduces new truncations | Stop as soon as rows fit |
| Column of pure footnote markers | Column isn't functioning as a column | Attach markers to key column, drop the column |
| Uniform column kept in table | Constant data isn't tabular data | Move to a note below the table |

---

## Reference Files

Detailed reference material in `references/`:

- **[width-budget-cheatsheet.md](references/width-budget-cheatsheet.md)** — Platform width measurements, VS Code font metrics, quick-select guide
- **[symbol-reference.md](references/symbol-reference.md)** — Full Unicode symbol table, cross-platform compatibility matrix, copy-paste palette
- **[before-after-examples.md](references/before-after-examples.md)** — 6 complete transformation examples with techniques annotated
