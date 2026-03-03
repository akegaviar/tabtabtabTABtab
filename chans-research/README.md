# chans-research

Models can read APIs, but imageboards are a mess — 10 different engines, encoding quirks (cp932, EUC-JP), rate limits, ephemeral threads, HTML-in-JSON markup. This skill normalizes 20 sites behind one CLI so you can browse, ingest, search, and export without writing adapter code every time.

## What it does

- Browse catalogs and threads across 20 imageboard and forum sites
- Ingest board catalogs into a local SQLite database with FTS5 full-text search
- Search across all ingested data — works with CJK text (Japanese, Korean, Chinese)
- Export threads and search results to markdown
- Search FoolFuuka archives (desuarchive, 4plebs) via live API

## Supported sites

**Western (15):** 4chan, leftypol, wizchan, smuglo.li, uboachan, kissu.moe, sushigirl.us, 8kun, kohlchan, endchan, zzzchan, trashchan, 2ch.hk, desuarchive, 4plebs

**Japanese (3):** 5ch.net, Shitaraba (jbbs), Machi BBS

**Korean (2):** DCInside, Arca.live

## Cost

Negligible token cost — the skill runs in `context: fork` and the heavy lifting is Python scripts hitting public APIs. The skill file itself is mostly reference documentation. No MCP servers, no external dependencies beyond `requests`.

## Architecture

Ten engine adapters normalize all sites to a canonical post schema:

```
scripts/
├── chans.py        # CLI entrypoint (argparse + commands)
├── adapters.py     # Site registry + 10 engine adapters (1500+ lines)
├── fetch.py        # HTTP client: per-domain rate limits, If-Modified-Since, retries
├── db.py           # SQLite + FTS5 storage with trigram tokenizer
├── html_strip.py   # HTML → plaintext (4 converters: vichan, lynxchan, dat, dcinside)
└── dat_parse.py    # 5ch dat format parser (subject.txt + thread.dat)
```

Data is stored in `~/.claude/cache/chans.db` (SQLite with WAL mode). FTS5 uses trigram tokenization for CJK support.

## Important notes

- All APIs are **read-only** — no posting capability
- Threads on live boards are **ephemeral** — export before they expire
- Content is **unmoderated** — expect raw language and NSFW content
- Only dependency: Python 3.10+ with `requests` (`pip install requests`)
- No authentication required — all supported APIs are public

## License

MIT
