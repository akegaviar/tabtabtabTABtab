#!/usr/bin/env python3
"""Multi-site imageboard research tool — CLI entrypoint."""

import argparse
import sys
from datetime import datetime
from pathlib import Path
from urllib.parse import urlparse

# Ensure scripts/ is importable when run directly
sys.path.insert(0, str(Path(__file__).parent))

from adapters import SITES, get_adapter
from db import ChansDB
from fetch import Fetcher

DEFAULT_OUTPUT = Path.cwd() / "chan-exports"


# ── helpers ───────────────────────────────────────────────────────────

def _get_db():
    return ChansDB()


def _get_fetcher():
    return Fetcher()


def _ts_fmt(ts):
    """Format unix timestamp for display."""
    if not ts:
        return ""
    return datetime.fromtimestamp(ts).strftime("%Y-%m-%d %H:%M")


def _truncate(text, length=80):
    """Truncate text to length, replacing newlines with spaces."""
    text = (text or "").replace("\n", " ").strip()
    if len(text) > length:
        return text[:length - 3] + "..."
    return text


def _ext_from_url(url):
    """Extract file extension from a URL."""
    path = urlparse(url).path
    ext = Path(path).suffix
    return ext if ext else ".jpg"


def _download_images(posts, assets_dir, fetcher=None):
    """Download full and thumbnail images for posts into assets_dir.

    Returns dict mapping original URLs to local relative paths (relative to
    assets_dir's parent, i.e. 'assets/filename').
    """
    assets_dir = Path(assets_dir)
    assets_dir.mkdir(parents=True, exist_ok=True)
    if fetcher is None:
        fetcher = Fetcher()

    url_map = {}  # original_url → local relative path
    count = 0

    for p in posts:
        pid = p["post_id"]
        for url_key, suffix in [("image_url", "full"), ("thumb_url", "thumb")]:
            url = p[url_key] if url_key in p.keys() else ""
            if not url:
                continue
            ext = _ext_from_url(url)
            fname = f"{pid}_{suffix}{ext}"
            local_path = assets_dir / fname
            if local_path.exists():
                url_map[url] = f"assets/{fname}"
                continue
            try:
                r = fetcher.get(url, max_retries=2)
                if r and r.status_code == 200:
                    local_path.write_bytes(r.content)
                    url_map[url] = f"assets/{fname}"
                    count += 1
            except Exception as e:
                print(f"  warning: failed to download {url}: {e}",
                      file=sys.stderr)

    print(f"  Downloaded {count} images to {assets_dir}/")
    return url_map


# ── commands ──────────────────────────────────────────────────────────

def cmd_sites(args):
    """List all supported sites."""
    print(f"{'Site':<25} {'Engine':<12} {'Boards':>8}")
    print("-" * 48)
    for domain, cfg in sorted(SITES.items()):
        n_boards = "API" if cfg.boards_path else str(len(cfg.default_boards))
        print(f"{domain:<25} {cfg.engine:<12} {n_boards:>8}")
    print(f"\n{len(SITES)} sites supported")


def cmd_boards(args):
    """List boards for a site. Fixes bug 1: no misleading column headers."""
    fetcher = _get_fetcher()
    adapter = get_adapter(args.site, fetcher)
    boards = adapter.fetch_boards()

    print(f"{'Board':<12} {'Title':<40}")
    print("-" * 55)
    for b in boards:
        bname = f"/{b['board']}/"
        print(f"{bname:<12} {b.get('title', ''):<40}")
    print(f"\n{len(boards)} boards on {args.site}")


def cmd_catalog(args):
    """Fetch catalog, ingest to DB, and display."""
    fetcher = _get_fetcher()
    adapter = get_adapter(args.site, fetcher)
    db = _get_db()

    # Seed If-Modified-Since from persistent cache
    cat_url = adapter.catalog_url(args.board)
    if cat_url:
        state = db.get_fetch_state(args.site, args.board)
        if state and state["last_modified"]:
            fetcher.set_last_modified(cat_url, state["last_modified"])

    posts = adapter.fetch_catalog(args.board)
    if posts is None:
        print("Not modified (304)")
        db.close()
        return
    if not posts:
        print(f"No threads found on /{args.board}/ at {args.site}")
        if SITES[args.site].engine == "foolfuuka":
            print("(FoolFuuka archives don't have catalogs — use search)")
        db.close()
        return

    db.upsert_posts(posts)

    # Persist Last-Modified for next run
    lm = fetcher.get_last_modified(cat_url) if cat_url else ""
    db.update_fetch_state(args.site, args.board, last_modified=lm or "")

    print(f"/{args.board}/ on {args.site} — {len(posts)} threads\n")
    for p in posts:
        tid = p["post_id"]
        sub = _truncate(p.get("subject", ""), 50)
        replies = p.get("reply_count", 0)
        images = p.get("image_count", 0)
        snippet = _truncate(p.get("comment", ""), 70)
        title = sub if sub else snippet
        pinned = " [pinned]" if p.get("is_pinned") else ""
        img_tag = " [img]" if p.get("image_url") else ""
        print(f"[{tid}] {title} ({replies}r/{images}i){pinned}{img_tag}")

    db.close()


def cmd_thread(args):
    """Fetch thread, ingest to DB, and display/export."""
    fetcher = _get_fetcher()
    adapter = get_adapter(args.site, fetcher)
    db = _get_db()

    posts = adapter.fetch_thread(args.board, args.thread)
    if posts is None:
        print("Not modified (304)")
        db.close()
        return
    if not posts:
        print(f"Thread {args.thread} not found on /{args.board}/ at {args.site}")
        db.close()
        return

    db.upsert_posts(posts)
    op = posts[0]

    # Build URL from registry, not from post data (fixes bug 2)
    url = adapter.thread_url(args.board, args.thread)
    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    sub = op.get("subject", "") or f"Thread {args.thread}"

    lines = [
        f"# /{args.board}/ — {sub}",
        "",
        f"Site: {args.site}",
        f"Board: /{args.board}/",
        f"Thread: {args.thread}",
        f"URL: {url}",
        f"Exported: {now}",
        f"Posts: {len(posts)} | Replies: {op.get('reply_count', len(posts)-1)}",
        "",
        "---",
        "",
    ]

    for i, p in enumerate(posts):
        heading = "## OP" if i == 0 else "###"
        author = p.get("author", "Anonymous")
        ts = _ts_fmt(p.get("timestamp", 0))
        pid = p["post_id"]
        sub_line = f"**{p['subject']}**\n\n" if p.get("subject") else ""
        comment = p.get("comment", "")
        image_url = p.get("image_url", "")
        lines.append(f"{heading} — {author} — {ts} — No.{pid}")
        lines.append("")
        if sub_line:
            lines.append(sub_line)
        if image_url:
            lines.append(f"![image]({image_url})")
            lines.append("")
        lines.append(comment)
        lines.append("")
        lines.append("---")
        lines.append("")

    content = "\n".join(lines)

    if args.stdout and not getattr(args, "download_images", False):
        print(content)
    else:
        out_dir = Path(args.output)
        out_dir.mkdir(parents=True, exist_ok=True)
        safe_site = args.site.replace(".", "_")
        safe_board = args.board.replace("/", "_")

        # Download images if requested
        if getattr(args, "download_images", False):
            assets_dir = out_dir / "assets"
            url_map = _download_images(posts, assets_dir, fetcher)
            # Replace CDN URLs with local paths in content
            for orig_url, local_path in url_map.items():
                content = content.replace(orig_url, local_path)

        fname = f"{safe_site}_{safe_board}_{args.thread}.md"
        out_path = out_dir / fname
        out_path.write_text(content)
        print(f"Exported to {out_path} ({len(posts)} posts)")

    db.close()


def cmd_search(args):
    """FTS5 search across ingested data, or live FoolFuuka search."""
    db = _get_db()

    # For FoolFuuka sites, do a live archive search
    if args.site and SITES.get(args.site, None) and \
       SITES[args.site].engine == "foolfuuka":
        fetcher = _get_fetcher()
        adapter = get_adapter(args.site, fetcher)
        board = args.board or (SITES[args.site].default_boards[0]
                               if SITES[args.site].default_boards else "g")
        posts = adapter.search(board, args.query)
        if posts:
            db.upsert_posts(posts)
            print(f"Archive search: {len(posts)} results from "
                  f"{args.site}/{board}\n")
            for p in posts:
                pid = p["post_id"]
                tid = p["thread_id"]
                sub = _truncate(p.get("subject", ""), 50)
                snippet = _truncate(p.get("comment", ""), 80)
                title = sub if sub else snippet
                ts = _ts_fmt(p.get("timestamp", 0))
                print(f"[{pid}] {title}")
                print(f"  thread:{tid} | {ts}")
                print()
        else:
            print(f"No archive results for '{args.query}' on {args.site}")
        db.close()
        return

    # FTS5 search on local DB
    results = db.search(args.query, site=args.site, board=args.board)
    if not results:
        print(f"No results for '{args.query}' in local database")
        print("Tip: ingest some boards first with: chans.py ingest --site X -B board1,board2")
        db.close()
        return

    print(f"Found {len(results)} result(s) for '{args.query}':\n")
    for r in results:
        pid = r["post_id"]
        tid = r["thread_id"]
        site = r["site"]
        board = r["board"]
        sub = _truncate(r["subject"], 50)
        snippet = _truncate(r["comment"], 100)
        ts = _ts_fmt(r["timestamp"])
        title = sub if sub else snippet[:60]
        is_op = " [OP]" if r["is_op"] else ""
        print(f"{site} /{board}/ [{pid}]{is_op} {title}")
        print(f"  thread:{tid} | {ts}")
        if not sub and snippet:
            print(f"  {snippet}")
        print()

    db.close()


def cmd_ingest(args):
    """Bulk ingest catalogs into SQLite."""
    boards = [b.strip() for b in args.boards.split(",")]
    fetcher = _get_fetcher()
    adapter = get_adapter(args.site, fetcher)
    db = _get_db()

    total = 0
    for board in boards:
        try:
            # Seed If-Modified-Since from persistent cache
            cat_url = adapter.catalog_url(board)
            if cat_url:
                state = db.get_fetch_state(args.site, board)
                if state and state["last_modified"]:
                    fetcher.set_last_modified(cat_url, state["last_modified"])

            posts = adapter.fetch_catalog(board)
            if posts is None:
                print(f"  /{board}/: not modified (304)")
                continue
            if not posts:
                print(f"  /{board}/: no threads")
                continue
            count = db.upsert_posts(posts)

            # Persist Last-Modified for next run
            lm = fetcher.get_last_modified(cat_url) if cat_url else ""
            db.update_fetch_state(args.site, board, last_modified=lm or "")
            total += count
            print(f"  /{board}/: {count} threads ingested")
        except Exception as e:
            print(f"  /{board}/: error — {e}", file=sys.stderr)

    print(f"\nIngested {total} threads from {args.site}")
    db.close()


def cmd_export(args):
    """Export search results to markdown files."""
    db = _get_db()
    results = db.search(args.query, site=args.site, board=args.board,
                        limit=args.limit)
    if not results:
        print(f"No results for '{args.query}'")
        db.close()
        return

    out_dir = Path(args.output)
    out_dir.mkdir(parents=True, exist_ok=True)

    # Group by thread
    threads = {}
    for r in results:
        key = (r["site"], r["board"], r["thread_id"])
        if key not in threads:
            threads[key] = []
        threads[key].append(r)

    now = datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    lines = [
        f"# Search results: {args.query}",
        f"Exported: {now}",
        f"Results: {len(results)} posts across {len(threads)} threads",
        "",
        "---",
        "",
    ]

    for (site, board, tid), posts in threads.items():
        lines.append(f"## {site} /{board}/ thread {tid}")
        lines.append("")
        for p in posts:
            author = p["author"]
            ts = _ts_fmt(p["timestamp"])
            pid = p["post_id"]
            sub = p["subject"]
            comment = p["comment"]
            image_url = p["image_url"] if "image_url" in p.keys() else ""
            is_op = " [OP]" if p["is_op"] else ""
            lines.append(f"### No.{pid}{is_op} — {author} — {ts}")
            lines.append("")
            if sub:
                lines.append(f"**{sub}**")
                lines.append("")
            if image_url:
                lines.append(f"![image]({image_url})")
                lines.append("")
            lines.append(comment)
            lines.append("")
            lines.append("---")
            lines.append("")

    content = "\n".join(lines)
    safe_query = "".join(c if c.isalnum() or c in " -_" else ""
                         for c in args.query)[:50].strip().replace(" ", "_")
    fname = f"search_{safe_query}.md"
    out_path = out_dir / fname
    out_path.write_text(content)
    print(f"Exported {len(results)} results to {out_path}")

    db.close()


def cmd_download(args):
    """Download images for a thread from the DB (or fetch first)."""
    fetcher = _get_fetcher()
    db = _get_db()

    # Check if thread is already in DB
    posts = db.get_thread(args.site, args.board, int(args.thread))
    if not posts:
        # Fetch it first
        adapter = get_adapter(args.site, fetcher)
        raw_posts = adapter.fetch_thread(args.board, args.thread)
        if not raw_posts:
            print(f"Thread {args.thread} not found on /{args.board}/ at {args.site}")
            db.close()
            return
        db.upsert_posts(raw_posts)
        posts = db.get_thread(args.site, args.board, int(args.thread))

    out_dir = Path(args.output)
    assets_dir = out_dir / "assets"
    url_map = _download_images(posts, assets_dir, fetcher)
    print(f"  {len(url_map)} image files in {assets_dir}/")

    db.close()


def cmd_stats(args):
    """Show DB statistics."""
    db = _get_db()
    rows = db.get_stats()
    if not rows:
        print("No data ingested yet.")
        print("Run: chans.py ingest --site 4chan.org -B g,biz")
        db.close()
        return

    print(f"{'Site':<25} {'Board':<10} {'Posts':>8} {'Threads':>8} "
          f"{'Last fetch':>18}")
    print("-" * 75)
    total_posts = 0
    total_threads = 0
    for r in rows:
        total_posts += r["total_posts"]
        total_threads += r["threads"] or 0
        lf = _ts_fmt(r["last_fetched"])
        print(f"{r['site']:<25} /{r['board']+'/':<9} {r['total_posts']:>8} "
              f"{r['threads'] or 0:>8} {lf:>18}")
    print("-" * 75)
    print(f"{'Total':<36} {total_posts:>8} {total_threads:>8}")
    print(f"\nDB: {db.db_path}")

    db.close()


# ── main ──────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Multi-site imageboard research tool",
        prog="chans.py",
    )
    sub = parser.add_subparsers(dest="command", required=True)

    # sites
    sub.add_parser("sites", help="List all supported sites")

    # boards
    p = sub.add_parser("boards", help="List boards for a site")
    p.add_argument("--site", "-s", default="4chan.org",
                   help="Site domain (default: 4chan.org)")

    # catalog
    p = sub.add_parser("catalog", help="Fetch and display board catalog")
    p.add_argument("--site", "-s", default="4chan.org")
    p.add_argument("--board", "-b", required=True,
                   help="Board name (use category/id for Shitaraba, e.g., computer/43680)")

    # thread
    p = sub.add_parser("thread", help="Fetch and export a thread")
    p.add_argument("--site", "-s", default="4chan.org")
    p.add_argument("--board", "-b", required=True,
                   help="Board name (use category/id for Shitaraba, e.g., computer/43680)")
    p.add_argument("--thread", "-t", required=True,
                   help="Thread ID")
    p.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT))
    p.add_argument("--stdout", action="store_true",
                   help="Print to stdout instead of file")
    p.add_argument("--download-images", "-D", action="store_true",
                   help="Download full+thumb images to assets/ dir")

    # search
    p = sub.add_parser("search", help="Search across ingested data")
    p.add_argument("--query", "-q", required=True, help="Search query")
    p.add_argument("--site", "-s", default=None,
                   help="Filter by site domain")
    p.add_argument("--board", "-b", default=None, help="Filter by board")

    # ingest
    p = sub.add_parser("ingest", help="Bulk ingest catalogs into DB")
    p.add_argument("--site", "-s", default="4chan.org")
    p.add_argument("--boards", "-B", required=True,
                   help="Comma-separated board names")

    # export
    p = sub.add_parser("export", help="Export search results to markdown")
    p.add_argument("--query", "-q", required=True)
    p.add_argument("--site", "-s", default=None)
    p.add_argument("--board", "-b", default=None)
    p.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT))
    p.add_argument("--limit", "-l", type=int, default=100)

    # download
    p = sub.add_parser("download", help="Download images for a thread")
    p.add_argument("--site", "-s", default="4chan.org")
    p.add_argument("--board", "-b", required=True)
    p.add_argument("--thread", "-t", required=True, help="Thread ID")
    p.add_argument("--output", "-o", default=str(DEFAULT_OUTPUT))

    # stats
    sub.add_parser("stats", help="Show DB statistics")

    args = parser.parse_args()

    cmds = {
        "sites": cmd_sites,
        "boards": cmd_boards,
        "catalog": cmd_catalog,
        "thread": cmd_thread,
        "search": cmd_search,
        "ingest": cmd_ingest,
        "export": cmd_export,
        "download": cmd_download,
        "stats": cmd_stats,
    }
    cmds[args.command](args)


if __name__ == "__main__":
    main()
