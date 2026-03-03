# Before/After Transformation Examples

Six transformations across different domains with techniques annotated.

---

## 1. Feature Comparison Compression (Healthcare)

**Problem:** 7-column facility comparison at 138 chars, wraps in VS Code source view.

**BEFORE (138 chars):**

```markdown
| Facility Type        | Emergency Dept | Surgical Suites | Imaging Center | Lab Services | Pharmacy     | Telehealth Support |
|----------------------|---------------|-----------------|----------------|-------------|--------------|-------------------|
| Regional Hospital    | Available     | Available       | Available      | Available   | Partial      | Available         |
| Community Clinic     | Not Available | Not Available   | Available      | Available   | Not Avail.   | Available         |
| Rural Health Center  | Available     | Not Available   | Not Available  | Available   | Not Avail.   | Available         |
| Urgent Care          | Available     | Not Available   | Available      | N/A         | N/A          | Not Available     |
```

**AFTER (92 chars):**

```markdown
| Facility Type       | Emerg | Surgical | Imaging | Lab | Pharmacy | Telehealth |
|---------------------|:-----:|:--------:|:-------:|:---:|:--------:|:----------:|
| Regional Hospital   | ✓     | ✓        | ✓       | ✓   | ○¹       | ✓          |
| Community Clinic    | ✗     | ✗        | ✓       | ✓   | ✗        | ✓          |
| Rural Health Center | ✓     | ✗        | ✗       | ✓   | ✗        | ✓          |
| Urgent Care         | ✓     | ✗        | ✓       | —   | —        | ✗          |

¹ Outpatient dispensing only; no compounding or IV preparation.
```

**Techniques:** text→symbols (saved ~46 chars), header abbreviation, center alignment for status, footnote for nuance, — for N/A vs ✗ for not supported.

---

## 2. Table Split

**Problem:** 9 columns impossible to fit in any reasonable viewport.

**BEFORE:**

```markdown
| Chain | Shared | Dedicated | Elastic | REST | WS | Archive | Trace | Debug |
|-------|--------|-----------|---------|------|-----|---------|-------|-------|
| Ethereum | Yes | Yes | Yes | Yes | Yes | Yes | Yes | Partial |
| Solana | Yes | Yes | No | Yes | Yes | No | No | No |
```

**AFTER (two 5-column tables):**

```markdown
**Node Deployment Options**

| Chain    | Shared | Dedicated | Elastic | Archive |
|----------|:------:|:---------:|:-------:|:-------:|
| Ethereum | ✓      | ✓         | ✓       | ✓       |
| Solana   | ✓      | ✓         | ✗       | ✗       |

**API Access**

| Chain    | REST | WS | Trace | Debug |
|----------|:----:|:--:|:-----:|:-----:|
| Ethereum | ✓    | ✓  | ✓     | ○     |
| Solana   | ✓    | ✓  | ✗     | ✗     |
```

**Techniques:** logical split (infrastructure vs API), repeated key column, descriptive sub-headings, symbol replacement.

---

## 3. Footnote Pattern (Database Comparison)

**Problem:** Cells need qualifiers that make them too wide.

**BEFORE:**

```markdown
| Feature         | PostgreSQL               | MySQL                   | SQLite                |
|-----------------|--------------------------|-------------------------|-----------------------|
| JSON support    | Full (jsonb, indexable)   | Partial (JSON type only) | Text storage only     |
| Full-text search| Built-in (tsvector)      | Built-in (FULLTEXT)      | Extension (FTS5)      |
| Replication     | Streaming + logical      | Built-in (group, async)  | Not supported         |
| Max DB size     | Unlimited (tested to 32TB)| 256 TB                  | 281 TB                |
```

**AFTER (82 chars):**

```markdown
| Feature          | PostgreSQL | MySQL  | SQLite |
|------------------|:----------:|:------:|:------:|
| JSON support     | ✓¹         | ○²     | ✗³     |
| Full-text search | ✓⁴         | ✓⁵     | ○⁶     |
| Replication      | ✓⁷         | ✓⁸     | ✗      |
| Max DB size      | 32+ TB     | 256 TB | 281 TB |

¹ Full jsonb with GIN indexing.
² JSON type; no binary format or indexing.
³ Stored as text; no native JSON operators.
⁴ Built-in tsvector/tsquery.
⁵ Built-in FULLTEXT indexes.
⁶ Requires FTS5 extension.
⁷ Streaming + logical replication.
⁸ Group replication + async.
```

**Techniques:** footnotes preserve detail without widening cells, symbols for status, center-aligned status columns.

---

## 4. Transposed Table

**Problem:** Only 2 items to compare but 10+ attributes. A normal table would have 2 narrow data columns and a very tall key column, or 10+ columns if laid out horizontally.

**BEFORE (tall, hard to scan):**

```markdown
| Feature | Plan A | Plan B |
|---------|--------|--------|
| Price | $29/mo | $99/mo |
| Requests | 10M | 100M |
| Support | Email | Priority |
| SLA | 99.9% | 99.99% |
| Nodes | 3 | Unlimited |
| Archive | ✗ | ✓ |
| Trace | ✗ | ✓ |
| Debug | ✗ | ✓ |
| WebSocket | ✓ | ✓ |
| Dedicated | ✗ | ✓ |
```

**AFTER (grouped with visual breaks):**

```markdown
| Feature      | Growth  | Business    |
|--------------|---------|-------------|
| **Pricing**  |         |             |
| Monthly      | $29     | $99         |
| Requests     | 10M     | 100M        |
| SLA          | 99.9%   | 99.99%      |
| **Access**   |         |             |
| Nodes        | 3       | Unlimited   |
| Dedicated    | ✗       | ✓           |
| **Features** |         |             |
| Archive      | ✗       | ✓           |
| Trace        | ✗       | ✓           |
| Debug        | ✗       | ✓           |
| WebSocket    | ✓       | ✓           |
| Support      | Email   | Priority    |
```

**Techniques:** kept vertical layout but added bold row-group headers, renamed plans to meaningful names, reordered logically. Sometimes a vertical table is correct—just organize it well.

---

## 5. Sparse Table Condensation (CI/CD Tools)

**Problem:** Many cells are empty because most features only apply to a few items.

**BEFORE:**

```markdown
| Tool       | GitHub | GitLab | Bitbucket | Jenkins | CircleCI | Travis |
|------------|--------|--------|-----------|---------|----------|--------|
| GitHub Actions | Yes |        |           |         |          |        |
| GitLab CI  |        | Yes    |           |         |          |        |
| Pipelines  |        |        | Yes       |         |          |        |
| Jenkins    |        |        |           | Yes     |          |        |
| CircleCI   |        |        |           |         | Yes      |        |
| Travis CI  |        |        |           |         |          | Yes    |
```

**AFTER (condensed, no empty cells):**

```markdown
| Tool           | Platform  | Config Format | Self-Hosted |
|----------------|-----------|---------------|:-----------:|
| GitHub Actions | GitHub    | YAML          | ○¹          |
| GitLab CI      | GitLab    | YAML          | ✓           |
| Pipelines      | Bitbucket | YAML          | ✗           |
| Jenkins        | Any       | Groovy        | ✓           |
| CircleCI       | Any       | YAML          | ✓           |
| Travis CI      | Any       | YAML          | ✗           |

¹ Self-hosted runners only; server is cloud.
```

**Techniques:** recognized that sparse boolean matrix = 1:1 mapping, restructured as attribute columns instead of indicator columns. Added useful context (config format, self-hosted) that was implicit.

---

## 6. Legend Pattern

**Problem:** Multiple status levels need explanation but footnoting each would be excessive.

**BEFORE:**

```markdown
| Method | Ethereum (Shared) | Ethereum (Dedicated) | Polygon (Shared) | Polygon (Dedicated) |
|--------|-------------------|---------------------|-----------------|-------------------|
| eth_call | Rate limited, 25/sec | Unlimited | Rate limited, 50/sec | Unlimited |
| eth_getBalance | Rate limited, 25/sec | Unlimited | Rate limited, 50/sec | Unlimited |
| debug_trace | Not available | Available | Not available | Available, limited |
| eth_subscribe | Not available | Available | Available | Available |
```

**AFTER (86 chars):**

```markdown
| Method        | ETH Shared | ETH Dedicated | MATIC Shared | MATIC Dedicated |
|---------------|:----------:|:-------------:|:------------:|:---------------:|
| eth_call      | RL25       | ✓             | RL50         | ✓               |
| eth_getBalance| RL25       | ✓             | RL50         | ✓               |
| debug_trace   | ✗          | ✓             | ✗            | ○               |
| eth_subscribe | ✗          | ✓             | ✓            | ✓               |

**Legend:**
- ✓ = Available, no rate limit
- ✗ = Not available
- ○ = Available with restrictions
- RL25 = Rate limited to 25 req/sec
- RL50 = Rate limited to 50 req/sec
```

**Techniques:** coded abbreviations (RL25, RL50) with legend, shortened chain names in headers, center alignment, legend placed directly below table.
