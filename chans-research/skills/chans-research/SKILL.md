---
name: chans-research
description: Research imageboards and forums (4chan, 5ch, leftypol, kohlchan, endchan, zzzchan, 2ch.hk, DCInside, Arca.live, Machi BBS, Shitaraba + FoolFuuka archives). Use when the user wants to (1) browse boards and catalogs across sites, (2) search threads by keyword with FTS5, (3) export threads to markdown, or (4) search historical archives. No auth required.
context: fork
---

# Imageboard research tool

Browse, search, and export threads across 20 imageboard and forum sites.

## Prerequisites

- **Python 3.10+** with `requests` installed (`pip install requests`)

No authentication needed — all supported APIs are public and read-only.

## Supported sites

### Western

| Site | Engine | Notes |
|------|--------|-------|
| `4chan.org` | vichan | Boards API, CDN images |
| `leftypol.org` | vichan | Politics |
| `wizchan.org` | vichan | Male-only community |
| `smuglo.li` | vichan | Anime/manga community |
| `uboachan.net` | vichan | Yume Nikki/RPGMaker community |
| `kissu.moe` | vichan | Otaku culture |
| `sushigirl.us` | vichan | Comfy-posting community |
| `8kun.top` | vichan | Boards API (328 boards) |
| `kohlchan.net` | lynxchan | German-language imageboard |
| `endchan.net` | lynxchan | Free-speech focused |
| `zzzchan.xyz` | jschan | Misc boards |
| `trashchan.xyz` | jschan | Comfy/retro boards |
| `2ch.hk` | makaba | Largest Russian imageboard |
| `desuarchive.org` | foolfuuka | 4chan archive (search API) |
| `archive.4plebs.org` | foolfuuka | 4chan archive (search API) |

### Japanese

| Site | Engine | Notes |
|------|--------|-------|
| `5ch.net` | dat | Largest Japanese BBS. cp932 encoding. May return HTTP 451 from non-JP IPs |
| `jbbs.shitaraba.net` | shitaraba | Hosted boards. Board format: `category/id` (e.g., `computer/43680`). EUC-JP |
| `machi.to` | machibbs | Regional Japanese boards. JSON API, UTF-8 |

### Korean

| Site | Engine | Notes |
|------|--------|-------|
| `dcinside.com` | dcinside | Korean imageboard (283M monthly visits). Web scraping. Auto-detects gallery type (major/minor/mini) |
| `arca.live` | arcalive | Korean community platform (145M monthly visits). Mobile JSON API |

## Quick start

```bash
CHANS="python ${CLAUDE_PLUGIN_ROOT}/skills/chans-research/scripts/chans.py"

# List all supported sites
$CHANS sites

# List boards on a site
$CHANS boards --site 4chan.org
$CHANS boards --site 5ch.net

# Browse a board catalog
$CHANS catalog --site 4chan.org -b g
$CHANS catalog --site 5ch.net -b news4vip
$CHANS catalog --site machi.to -b tokyo
$CHANS catalog --site dcinside.com -b programming

# Export a thread to markdown
$CHANS thread --site 4chan.org -b biz -t 12345678
$CHANS thread --site machi.to -b tokyo -t 12345 --stdout

# Shitaraba uses category/id board format
$CHANS catalog --site jbbs.shitaraba.net -b computer/43680

# Bulk ingest boards into local SQLite
$CHANS ingest --site 4chan.org -B g,biz,sci
$CHANS ingest --site 5ch.net -B news4vip,poverty

# Search across all ingested data (FTS5) — works with CJK text
$CHANS search -q "artificial intelligence"
$CHANS search -q "テスト"
$CHANS search -q "bitcoin" --site 4chan.org --board biz

# Search FoolFuuka archives (live API, no ingest needed)
$CHANS search -q "bitcoin" --site desuarchive.org --board g

# Export search results to markdown
$CHANS export -q "machine learning" -o ./exports

# Show DB statistics
$CHANS stats
```

## Workflow

### 1. Discover sites and boards

```bash
$CHANS sites                           # all 20 supported sites
$CHANS boards --site 4chan.org         # all boards on 4chan
$CHANS boards --site 5ch.net          # all boards on 5ch (from bbsmenu)
```

### 2. Ingest data

```bash
$CHANS ingest --site 4chan.org -B g,biz,sci
$CHANS ingest --site 5ch.net -B news4vip,poverty
```

Ingestion fetches the full catalog for each board and stores all OP posts in a local SQLite database (`~/.claude/cache/chans.db`) with FTS5 indexing.

### 3. Search

```bash
$CHANS search -q "home server"
$CHANS search -q "rust programming" --site 4chan.org --board g
$CHANS search -q "テスト"              # CJK search works with FTS5
```

For archive sites (desuarchive, 4plebs), search hits the live FoolFuuka API and also ingests results locally.

### 4. Export threads

```bash
$CHANS thread --site 4chan.org -b g -t 12345678 --stdout
$CHANS thread --site machi.to -b tokyo -t 12345 --stdout
```

## Architecture

```
scripts/
├── chans.py        # CLI entrypoint (argparse + commands)
├── adapters.py     # Site registry + 10 engine adapters
├── fetch.py        # HTTP: rate limits, If-Modified-Since, retries
├── db.py           # SQLite + FTS5 storage
├── html_strip.py   # HTML → plaintext (vichan, lynxchan, dat, dcinside)
└── dat_parse.py    # 2ch/5ch dat format parser (subject.txt + thread.dat)
```

**10 engine adapter families** normalize all sites to a canonical post schema:

- **VichanAdapter** — 4chan, leftypol, wizchan, smuglo.li, uboachan, kissu.moe, sushigirl.us, 8kun.top
- **LynxchanAdapter** / **JschanAdapter** — kohlchan, endchan, zzzchan, trashchan
- **MakabaAdapter** — 2ch.hk (Russian)
- **FoolFuukaAdapter** — desuarchive, 4plebs (search-only archives)
- **DatAdapter** — 5ch.net (Japanese dat format, server discovery via bbsmenu)
- **ShitarabaAdapter** — jbbs.shitaraba.net (EUC-JP, category/id boards)
- **MachiBBSAdapter** — machi.to (JSON API, regional Japanese boards)
- **DCInsideAdapter** — dcinside.com (Korean, web HTML scraping, auto-detects gallery type)
- **ArcaLiveAdapter** — arca.live (Korean, mobile JSON API)

## API rate limits

Western sites default to 1 req/s. Japanese sites use 1.5-2.0s. Korean sites use 1.5s. The fetch layer enforces per-domain rate limiting automatically. Repeat requests to the same URL use `If-Modified-Since` to avoid re-downloading unchanged data.

## Important notes

- All APIs are **read-only** — no posting capability
- Threads on live boards are **ephemeral** — export promptly before archival
- Content is **unmoderated** — expect raw language and NSFW content
- Archive sites (FoolFuuka) have **permanent** storage but search-only access
- Data is stored locally in `~/.claude/cache/chans.db` (SQLite with WAL mode)
- **5ch.net** may return HTTP 451 from non-Japanese IPs — the adapter handles this gracefully
- **Shitaraba** boards use `category/id` format (e.g., `computer/43680`)
- FTS5 search works with CJK text (Japanese, Korean, Chinese). Queries of 3+ characters use the trigram index; shorter queries fall back to LIKE
