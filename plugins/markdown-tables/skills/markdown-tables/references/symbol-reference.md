# Symbol Reference

## Primary Symbol Set

Copy-paste ready. These are the recommended defaults:

```
✓  ✗  —  ○  ●
```

| Symbol | Unicode | Name | Meaning |
|:------:|---------|------|---------|
| ✓ | U+2713 | Check Mark | Yes, supported, pass |
| ✗ | U+2717 | Ballot X | No, unsupported, fail |
| — | U+2014 | Em Dash | Not applicable, N/A |
| ○ | U+25CB | White Circle | Partial, in progress |
| ● | U+25CF | Black Circle | Full, complete |

---

## Extended Symbol Set

For more nuanced tables:

| Symbol | Unicode | Name | Suggested Use |
|:------:|---------|------|---------------|
| △ | U+25B3 | White Triangle | Warning, caution |
| ▲ | U+25B2 | Black Triangle | Critical, alert |
| ★ | U+2605 | Black Star | Featured, recommended |
| ☆ | U+2606 | White Star | Notable, secondary |
| → | U+2192 | Right Arrow | See also, redirects to |
| ↑ | U+2191 | Up Arrow | Increased, improved |
| ↓ | U+2193 | Down Arrow | Decreased, degraded |
| ~ | U+007E | Tilde | Approximately |

---

## Cross-Platform Compatibility

| Symbol | VS Code | GitHub | Obsidian | Terminal | macOS | Windows | Linux |
|:------:|:-------:|:------:|:--------:|:--------:|:-----:|:-------:|:-----:|
| ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ✗ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| — | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ○ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ● | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ | ✓ |
| ✅ | ✓ | ✓ | ✓ | ○ | ✓ | ○ | ○ |
| ❌ | ✓ | ✓ | ✓ | ○ | ✓ | ○ | ○ |
| ⚠️ | ✓ | ✓ | ✓ | ○ | ✓ | ○ | ○ |

**Key:** ✓ Renders correctly | ○ May render differently | ✗ Fails to render

Emoji (✅❌⚠️) have inconsistent width in monospace fonts and can misalign columns. Prefer text symbols for source-view tables.

---

## Footnote Markers

Use Unicode superscript numbers for footnotes:

```
¹  ²  ³  ⁴  ⁵  ⁶  ⁷  ⁸  ⁹
```

| Marker | Unicode | Usage |
|:------:|---------|-------|
| ¹ | U+00B9 | Superscript One |
| ² | U+00B2 | Superscript Two |
| ³ | U+00B3 | Superscript Three |
| ⁴ | U+2074 | Superscript Four |
| ⁵ | U+2075 | Superscript Five |
| ⁶ | U+2076 | Superscript Six |
| ⁷ | U+2077 | Superscript Seven |
| ⁸ | U+2078 | Superscript Eight |
| ⁹ | U+2079 | Superscript Nine |

For 10+, combine: ¹⁰ ¹¹ ¹² (U+00B9 + U+2070, etc.)

---

## Copy-Paste Palette

Quick-copy blocks for common table scenarios:

**Status table:**
```
✓  ✗  —  ○
```

**Footnoted cell:**
```
✓¹  ✗²  ○³
```

**Legend line:**
```
**Legend:** ✓ Supported | ✗ Not supported | ○ Partial | — N/A
```

**Alignment row (6 columns, center-aligned):**
```
|:---:|:---:|:---:|:---:|:---:|:---:|
```

**Alignment row (mixed: left, center×4, right):**
```
|:---|:---:|:---:|:---:|:---:|---:|
```
