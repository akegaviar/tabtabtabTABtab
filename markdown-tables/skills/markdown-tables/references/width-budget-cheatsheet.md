# Width Budget Cheatsheet

## VS Code Source View Widths

Measured at default font size (14px, Menlo/Consolas) with sidebar open:

| Screen | Resolution | Sidebar | Usable Editor | Chars (14px) | Chars (12px) |
|--------|-----------|---------|---------------|:------------:|:------------:|
| 16" MBP | 3456×2234 | 250px | ~1100px | **~120** | ~140 |
| 14" MBP | 3024×1964 | 250px | ~900px | **~100** | ~115 |
| 13" MBP | 2560×1600 | 250px | ~750px | **~85** | ~100 |
| 27" ext | 2560×1440 | 250px | ~1200px | **~130** | ~150 |
| 24" ext | 1920×1080 | 250px | ~850px | **~95** | ~110 |

### Font Size Impact

| Font Size | Char Width (Menlo) | Chars in 1100px |
|-----------|-------------------|:---------------:|
| 12px | ~7.2px | ~152 |
| 13px | ~7.8px | ~141 |
| **14px** | **~8.4px** | **~131** |
| 15px | ~9.0px | ~122 |
| 16px | ~9.6px | ~114 |

### VS Code Minimap

With minimap enabled (default), subtract ~120px from usable editor width (~13 chars at 14px).

---

## Platform Rendering Widths

| Platform | Max Comfortable Width | Notes |
|----------|:--------------------:|-------|
| **VS Code** (source) | **120** | Default target. 14px Menlo, 16" MBP |
| **GitHub** (README) | **110** | Fixed-width content area, ~900px |
| **GitHub** (file view) | **115** | Slightly wider than README |
| **Obsidian** (reading) | **100** | Depends on theme; narrow default pane |
| **Obsidian** (source) | **110** | Similar to VS Code but narrower pane |
| **MkDocs Material** | **140** | Wide content area, good for docs sites |
| **Terminal** (80 col) | **80** | Traditional terminal width |
| **Terminal** (120 col) | **120** | Wide terminal, matches VS Code |
| **Confluence** | **130** | Wide layout but tables have own scroll |
| **Notion** | **100** | Narrow content column |

---

## Quick Select

Pick your target:

```
"I'm writing for..."

  VS Code (my own files)     → 120 chars
  GitHub README              → 110 chars
  Multi-platform docs        → 100 chars (safe everywhere)
  Documentation site         → 140 chars
  Terminal/CLI output        → 80 chars
  Unknown/safest             → 100 chars
```

---

## Width Estimation Shortcut

For quick mental math:

```
Per-column overhead: 3 chars (space + pipe + space)
Plus 1 trailing pipe

Rule of thumb:
  120 target - (columns × 3) - 1 = chars available for content

  5 columns: 120 - 16 = 104 chars for content → ~21 per column
  6 columns: 120 - 19 = 101 chars for content → ~17 per column
  7 columns: 120 - 22 = 98 chars for content  → ~14 per column
  8 columns: 120 - 25 = 95 chars for content  → ~12 per column
```

---

## Split-View Considerations

When VS Code is in split view (two editors side by side):

| Config | Available Width | Recommended Target |
|--------|:--------------:|:------------------:|
| 50/50 split | ~550px | **65 chars** |
| 70/30 split (main) | ~770px | **85 chars** |
| 70/30 split (side) | ~330px | **38 chars** (avoid tables) |

In split view, strongly prefer narrow tables (4-5 columns, short content) or use lists instead.
