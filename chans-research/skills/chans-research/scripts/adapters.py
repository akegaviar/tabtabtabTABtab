"""Site registry and engine adapters for imageboard APIs."""

import re
import time
from dataclasses import dataclass, field
from datetime import datetime, timezone, timedelta
from urllib.parse import quote

from html_strip import strip_html, strip_lynxchan_html, strip_dat_html, strip_dcinside_html


@dataclass
class SiteConfig:
    """Configuration for a supported imageboard site."""
    domain: str
    engine: str  # vichan, lynxchan, jschan, foolfuuka, dat, shitaraba, machibbs, dcinside, makaba, arcalive
    api_base: str
    board_url: str  # web URL pattern for boards
    thread_url: str  # web URL pattern for threads
    catalog_path: str  # API path: /{board}/catalog.json
    thread_path: str  # API path: /{board}/thread/{id}.json
    boards_path: str = ""  # API path for board list (empty = not available)
    rate_limit: float = 1.0
    default_boards: list = field(default_factory=list)
    extra: dict = field(default_factory=dict)  # adapter-specific config


# ── Site registry ─────────────────────────────────────────────────────

SITES = {
    # ── vichan family ──
    "4chan.org": SiteConfig(
        domain="4chan.org",
        engine="vichan",
        api_base="https://a.4cdn.org",
        board_url="https://boards.4chan.org/{board}/",
        thread_url="https://boards.4chan.org/{board}/thread/{thread_id}",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/thread/{thread_id}.json",
        boards_path="/boards.json",
        rate_limit=1.0,
        extra={
            "image_base": "https://i.4cdn.org",
            "image_path": "/{board}/{tim}{ext}",
            "thumb_path": "/{board}/{tim}s.jpg",
        },
    ),
    "leftypol.org": SiteConfig(
        domain="leftypol.org",
        engine="vichan",
        api_base="https://leftypol.org",
        board_url="https://leftypol.org/{board}/",
        thread_url="https://leftypol.org/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["leftypol", "siberia", "hobby", "tech", "edu",
                         "games", "anime", "music", "draw", "AKM"],
    ),
    "wizchan.org": SiteConfig(
        domain="wizchan.org",
        engine="vichan",
        api_base="https://wizchan.org",
        board_url="https://wizchan.org/{board}/",
        thread_url="https://wizchan.org/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["wiz", "dep", "hob", "lounge", "jp", "meta",
                         "games", "music"],
    ),
    "smuglo.li": SiteConfig(
        domain="smuglo.li",
        engine="vichan",
        api_base="https://smuglo.li",
        board_url="https://smuglo.li/{board}/",
        thread_url="https://smuglo.li/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["a", "rec", "vg", "support"],
    ),
    "uboachan.net": SiteConfig(
        domain="uboachan.net",
        engine="vichan",
        api_base="https://uboachan.net",
        board_url="https://uboachan.net/{board}/",
        thread_url="https://uboachan.net/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["yn", "ot", "n", "hikki", "media", "o", "fg", "flow",
                         "cos", "lit", "og"],
    ),
    "kissu.moe": SiteConfig(
        domain="kissu.moe",
        engine="vichan",
        api_base="https://kissu.moe",
        board_url="https://kissu.moe/{board}/",
        thread_url="https://kissu.moe/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["qa", "jp", "b", "chat", "ec", "trans", "megu"],
    ),
    "sushigirl.us": SiteConfig(
        domain="sushigirl.us",
        engine="vichan",
        api_base="https://sushigirl.us",
        board_url="https://sushigirl.us/{board}/",
        thread_url="https://sushigirl.us/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["lounge", "arcade", "kawaii", "kitchen", "tunes",
                         "culture", "silicon", "otaku", "hell", "yakuza"],
    ),

    # ── lynxchan family ──
    "kohlchan.net": SiteConfig(
        domain="kohlchan.net",
        engine="lynxchan",
        api_base="https://kohlchan.net",
        board_url="https://kohlchan.net/{board}/",
        thread_url="https://kohlchan.net/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["int", "b", "meta"],
    ),
    "endchan.net": SiteConfig(
        domain="endchan.net",
        engine="lynxchan",
        api_base="https://endchan.net",
        board_url="https://endchan.net/{board}/",
        thread_url="https://endchan.net/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["ausneets", "polru", "yuri", "agatha2"],
    ),
    "8kun.top": SiteConfig(
        domain="8kun.top",
        engine="vichan",
        api_base="https://8kun.top",
        board_url="https://8kun.top/{board}/",
        thread_url="https://8kun.top/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        boards_path="/boards.json",
        rate_limit=1.0,
        default_boards=["pnd", "qresearch", "random", "pol", "v"],
        extra={
            "image_base": "https://media.8kun.top",
            "image_path": "/file_store/{tim}{ext}",
            "thumb_path": "/file_store/thumb/{tim}{ext}",
        },
    ),

    # ── jschan ──
    "zzzchan.xyz": SiteConfig(
        domain="zzzchan.xyz",
        engine="jschan",
        api_base="https://zzzchan.xyz",
        board_url="https://zzzchan.xyz/{board}/",
        thread_url="https://zzzchan.xyz/{board}/thread/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/thread/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["b", "v", "tech"],
    ),
    "trashchan.xyz": SiteConfig(
        domain="trashchan.xyz",
        engine="jschan",
        api_base="https://trashchan.xyz",
        board_url="https://trashchan.xyz/{board}/",
        thread_url="https://trashchan.xyz/{board}/thread/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/thread/{thread_id}.json",
        rate_limit=1.0,
        default_boards=["meta", "comfy", "retro"],
    ),

    # ── makaba ──
    "2ch.hk": SiteConfig(
        domain="2ch.hk",
        engine="makaba",
        api_base="https://2ch.org",
        board_url="https://2ch.hk/{board}/",
        thread_url="https://2ch.hk/{board}/res/{thread_id}.html",
        catalog_path="/{board}/catalog.json",
        thread_path="/{board}/res/{thread_id}.json",
        boards_path="/api/mobile/v2/boards",
        rate_limit=1.0,
        default_boards=["b", "po", "hw", "soc", "media", "rf", "int"],
    ),

    # ── FoolFuuka archives ──
    "desuarchive.org": SiteConfig(
        domain="desuarchive.org",
        engine="foolfuuka",
        api_base="https://desuarchive.org",
        board_url="https://desuarchive.org/{board}/",
        thread_url="https://desuarchive.org/{board}/thread/{thread_id}",
        catalog_path="",  # no catalog — search only
        thread_path="/_/api/chan/thread/?board={board}&num={thread_id}",
        rate_limit=1.0,
        default_boards=["g", "a", "co", "his", "int", "k", "m", "tg",
                         "mlp", "tv", "x"],
    ),
    "archive.4plebs.org": SiteConfig(
        domain="archive.4plebs.org",
        engine="foolfuuka",
        api_base="https://archive.4plebs.org",
        board_url="https://archive.4plebs.org/{board}/",
        thread_url="https://archive.4plebs.org/{board}/thread/{thread_id}",
        catalog_path="",
        thread_path="/_/api/chan/thread/?board={board}&num={thread_id}",
        rate_limit=1.0,
        default_boards=["adv", "f", "hr", "o", "pol", "s4s", "sp", "tg",
                         "trv", "tv", "x"],
    ),
    # ── dat family (5ch/2ch) ──
    "5ch.net": SiteConfig(
        domain="5ch.net",
        engine="dat",
        api_base="https://5ch.net",
        board_url="https://{server}.5ch.net/{board}/",
        thread_url="https://{server}.5ch.net/test/read.cgi/{board}/{thread_id}",
        catalog_path="/{board}/subject.txt",
        thread_path="/{board}/dat/{thread_id}.dat",
        rate_limit=2.0,
        default_boards=["newsplus", "poverty", "livejupiter", "news4vip"],
        extra={
            "bbsmenu_url": "https://menu.5ch.net/bbsmenu.json",
            "bbsmenu_format": "json",
            "encoding": "cp932",
            "user_agent": "Monazilla/1.00 (chans-research/2.0)",
        },
    ),
    # ── Shitaraba ──
    "jbbs.shitaraba.net": SiteConfig(
        domain="jbbs.shitaraba.net",
        engine="shitaraba",
        api_base="https://jbbs.shitaraba.net",
        board_url="https://jbbs.shitaraba.net/{board}/",
        thread_url="https://jbbs.shitaraba.net/bbs/read.cgi/{board}/{thread_id}",
        catalog_path="/{board}/subject.txt",
        thread_path="/bbs/rawmode.cgi/{board}/{thread_id}/",
        rate_limit=1.5,
        default_boards=["computer/43680", "internet/20196", "game/60338"],
        extra={"encoding": "euc-jp"},
    ),

    # ── Machi BBS ──
    "machi.to": SiteConfig(
        domain="machi.to",
        engine="machibbs",
        api_base="https://machi.to",
        board_url="https://machi.to/{board}/",
        thread_url="https://machi.to/bbs/read.cgi/{board}/{thread_id}",
        catalog_path="/bbs/json.cgi/{board}/",
        thread_path="/bbs/json.cgi/{board}/{thread_id}/",
        rate_limit=1.5,
        default_boards=["hokkaidou", "tohoku", "kanto", "tokyo", "tokai",
                         "kinki", "osaka", "chugoku", "sikoku", "kyusyu",
                         "okinawa"],
    ),

    # ── DCInside (Korea) ──
    "dcinside.com": SiteConfig(
        domain="dcinside.com",
        engine="dcinside",
        api_base="https://gall.dcinside.com",
        board_url="https://gall.dcinside.com/mgallery/board/lists/?id={board}",
        thread_url="https://gall.dcinside.com/mgallery/board/view/?id={board}&no={thread_id}",
        catalog_path="/mgallery/board/lists/?id={board}",
        thread_path="/mgallery/board/view/?id={board}&no={thread_id}",
        rate_limit=1.5,
        default_boards=["war", "hit", "programming", "computer"],
        extra={
            "user_agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
        },
    ),

    # ── Arca.live (Korea) ──
    "arca.live": SiteConfig(
        domain="arca.live",
        engine="arcalive",
        api_base="https://arca.live",
        board_url="https://arca.live/b/{board}",
        thread_url="https://arca.live/b/{board}/{thread_id}",
        catalog_path="/api/app/list/channel/{board}",
        thread_path="/api/app/view/article/breaking/{thread_id}",
        rate_limit=1.5,
        default_boards=["breaking", "headline", "society", "military815", "themilitary"],
        extra={
            "user_agent": "net.umanle.arca.android.playstore/0.9.75",
        },
    ),

}


# ── Adapters ──────────────────────────────────────────────────────────

def _now_ts():
    return int(time.time())


class VichanAdapter:
    """Adapter for vichan/4chan-style APIs."""

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )

    def _url(self, path, **kwargs):
        return self.site.api_base + path.format(**kwargs)

    def fetch_boards(self):
        """Fetch board list. Returns list of dicts or default_boards."""
        if self.site.boards_path:
            data = self.fetcher.get_json(self._url(self.site.boards_path))
            if data and isinstance(data, dict) and "boards" in data:
                return [
                    {"board": b["board"], "title": b.get("title", ""),
                     "pages": b.get("pages", 0)}
                    for b in data["boards"]
                ]
            # 8kun-style: flat list with "uri" key
            if data and isinstance(data, list) and data and "uri" in data[0]:
                return [
                    {"board": b["uri"], "title": b.get("title", "").strip(),
                     "pages": 0}
                    for b in data
                ]
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def fetch_catalog(self, board):
        """Fetch catalog and return normalized posts (OP posts only)."""
        url = self._url(self.site.catalog_path, board=board)
        data = self.fetcher.get_json(url)
        if data is None:
            return None  # 304
        posts = []
        for page in data:
            for t in page.get("threads", []):
                posts.append(self._normalize_catalog_post(t, board))
        return posts

    def fetch_thread(self, board, thread_id):
        """Fetch full thread and return normalized posts."""
        url = self._url(self.site.thread_path, board=board,
                        thread_id=thread_id)
        data = self.fetcher.get_json(url)
        if data is None:
            return None
        raw_posts = data.get("posts", [])
        posts = []
        for i, p in enumerate(raw_posts):
            posts.append(self._normalize_post(p, board, thread_id,
                                              is_op=(i == 0)))
        return posts

    def _image_urls(self, p, board):
        """Build full and thumbnail image URLs from a vichan post dict."""
        tim = p.get("tim")
        ext = p.get("ext")
        if not tim or not ext:
            return "", ""
        image_base = self.site.extra.get("image_base", self.site.api_base)
        image_path = self.site.extra.get(
            "image_path", "/{board}/src/{tim}{ext}")
        thumb_path = self.site.extra.get(
            "thumb_path", "/{board}/thumb/{tim}s.jpg")
        image_url = image_base + image_path.format(
            board=board, tim=tim, ext=ext)
        thumb_url = image_base + thumb_path.format(
            board=board, tim=tim, ext=ext)
        return image_url, thumb_url

    def _normalize_catalog_post(self, t, board):
        """Normalize a catalog thread entry to canonical schema."""
        image_url, thumb_url = self._image_urls(t, board)
        return {
            "post_id": t["no"],
            "thread_id": t["no"],
            "board": board,
            "site": self.site.domain,
            "subject": t.get("sub", ""),
            "comment": strip_html(t.get("com", "")),
            "author": t.get("name", "Anonymous"),
            "timestamp": t.get("time", 0),
            "reply_count": t.get("replies", 0),
            "image_count": t.get("images", 0),
            "is_op": 1,
            "is_pinned": 1 if t.get("sticky") else 0,
            "is_closed": 1 if t.get("closed") else 0,
            "fetched_at": _now_ts(),
            "image_url": image_url,
            "thumb_url": thumb_url,
        }

    def _normalize_post(self, p, board, thread_id, is_op=False):
        """Normalize a single post to canonical schema."""
        image_url, thumb_url = self._image_urls(p, board)
        return {
            "post_id": p["no"],
            "thread_id": thread_id,
            "board": board,
            "site": self.site.domain,
            "subject": p.get("sub", ""),
            "comment": strip_html(p.get("com", "")),
            "author": p.get("name", "Anonymous"),
            "timestamp": p.get("time", 0),
            "reply_count": p.get("replies", 0) if is_op else 0,
            "image_count": p.get("images", 0) if is_op else (
                1 if "tim" in p else 0
            ),
            "is_op": 1 if is_op else 0,
            "is_pinned": 1 if p.get("sticky") else 0,
            "is_closed": 1 if p.get("closed") else 0,
            "fetched_at": _now_ts(),
            "image_url": image_url,
            "thumb_url": thumb_url,
        }

    def catalog_url(self, board):
        return self._url(self.site.catalog_path, board=board)

    def thread_url(self, board, thread_id):
        """Build web URL for a thread from registry (fixes bug 2)."""
        return self.site.thread_url.format(board=board, thread_id=thread_id)


class LynxchanAdapter:
    """Adapter for LynxChan-style APIs (Kohlchan, Endchan)."""

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )

    def _url(self, path, **kwargs):
        return self.site.api_base + path.format(**kwargs)

    def fetch_boards(self):
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def fetch_catalog(self, board):
        url = self._url(self.site.catalog_path, board=board)
        data = self.fetcher.get_json(url)
        if data is None:
            return None
        posts = []
        # LynxChan catalog is a flat list of thread objects
        threads = data if isinstance(data, list) else data.get("threads", data)
        if isinstance(threads, dict):
            threads = threads.get("threads", [])
        for t in threads:
            posts.append(self._normalize_thread(t, board))
        return posts

    def fetch_thread(self, board, thread_id):
        url = self._url(self.site.thread_path, board=board,
                        thread_id=thread_id)
        data = self.fetcher.get_json(url)
        if data is None:
            return None
        posts = []
        # OP
        posts.append(self._normalize_post(data, board, thread_id, is_op=True))
        # Replies
        for p in data.get("posts", []):
            posts.append(self._normalize_post(p, board, thread_id,
                                              is_op=False))
        return posts

    def _parse_timestamp(self, raw):
        """Parse LynxChan ISO timestamp to unix int."""
        if isinstance(raw, (int, float)):
            return int(raw)
        if not raw:
            return 0
        try:
            # ISO format: 2024-01-15T12:30:00.000Z
            raw = str(raw).replace("Z", "+00:00")
            dt = datetime.fromisoformat(raw)
            return int(dt.timestamp())
        except (ValueError, TypeError):
            return 0

    def _image_urls(self, p):
        """Extract first file URL from a LynxChan post."""
        files = p.get("files") or []
        if not files:
            return "", ""
        f = files[0]
        path = f.get("path", "")
        thumb = f.get("thumb", "")
        base = self.site.api_base
        image_url = (base + path) if path and path.startswith("/") else path
        thumb_url = (base + thumb) if thumb and thumb.startswith("/") else thumb
        return image_url or "", thumb_url or ""

    def _normalize_thread(self, t, board):
        tid = t.get("threadId", t.get("postId", t.get("no", 0)))
        image_url, thumb_url = self._image_urls(t)
        return {
            "post_id": tid,
            "thread_id": tid,
            "board": board,
            "site": self.site.domain,
            "subject": t.get("subject", ""),
            "comment": strip_lynxchan_html(t.get("message", t.get("markdown", ""))),
            "author": t.get("name", "Anonymous"),
            "timestamp": self._parse_timestamp(
                t.get("lastBump", t.get("creation", ""))
            ),
            "reply_count": t.get("postCount", t.get("ommitedPosts", 0)),
            "image_count": t.get("fileCount", 0),
            "is_op": 1,
            "is_pinned": 1 if t.get("pinned") else 0,
            "is_closed": 1 if t.get("locked") else 0,
            "fetched_at": _now_ts(),
            "image_url": image_url,
            "thumb_url": thumb_url,
        }

    def _normalize_post(self, p, board, thread_id, is_op=False):
        pid = p.get("postId", p.get("threadId", p.get("no", 0)))
        image_url, thumb_url = self._image_urls(p)
        return {
            "post_id": pid,
            "thread_id": thread_id,
            "board": board,
            "site": self.site.domain,
            "subject": p.get("subject", ""),
            "comment": strip_lynxchan_html(p.get("message", p.get("markdown", ""))),
            "author": p.get("name", "Anonymous"),
            "timestamp": self._parse_timestamp(p.get("creation", "")),
            "reply_count": p.get("postCount", 0) if is_op else 0,
            "image_count": len(p.get("files") or []),
            "is_op": 1 if is_op else 0,
            "is_pinned": 1 if p.get("pinned") else 0,
            "is_closed": 1 if p.get("locked") else 0,
            "fetched_at": _now_ts(),
            "image_url": image_url,
            "thumb_url": thumb_url,
        }

    def catalog_url(self, board):
        return self._url(self.site.catalog_path, board=board)

    def thread_url(self, board, thread_id):
        return self.site.thread_url.format(board=board, thread_id=thread_id)


class JschanAdapter(LynxchanAdapter):
    """Adapter for jschan-style APIs (zzzchan). Similar to LynxChan."""

    def fetch_catalog(self, board):
        url = self._url(self.site.catalog_path, board=board)
        data = self.fetcher.get_json(url)
        if data is None:
            return None
        posts = []
        # jschan catalog can be flat list or have threads key
        threads = data if isinstance(data, list) else data.get("threads", [])
        for t in threads:
            posts.append(self._normalize_thread(t, board))
        return posts


class MakabaAdapter:
    """Adapter for Makaba engine (2ch.hk / Dvach)."""

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )

    def _url(self, path, **kwargs):
        return self.site.api_base + path.format(**kwargs)

    def fetch_boards(self):
        if self.site.boards_path:
            data = self.fetcher.get_json(self._url(self.site.boards_path))
            if data and isinstance(data, list):
                return [
                    {"board": b["id"], "title": b.get("name", ""),
                     "pages": b.get("max_pages", 0)}
                    for b in data
                ]
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def fetch_catalog(self, board):
        url = self._url(self.site.catalog_path, board=board)
        data = self.fetcher.get_json(url)
        if data is None:
            return None
        posts = []
        for t in data.get("threads", []):
            posts.append(self._normalize_catalog_post(t, board))
        return posts

    def fetch_thread(self, board, thread_id):
        url = self._url(self.site.thread_path, board=board,
                        thread_id=thread_id)
        data = self.fetcher.get_json(url)
        if data is None:
            return None
        posts = []
        for thread_obj in data.get("threads", []):
            for i, p in enumerate(thread_obj.get("posts", [])):
                posts.append(self._normalize_post(p, board, thread_id,
                                                  is_op=(i == 0)))
        return posts

    def _image_urls(self, p):
        """Extract first file URL from a Makaba post."""
        files = p.get("files") or []
        if not files:
            return "", ""
        f = files[0]
        path = f.get("path", "")
        thumb = f.get("thumbnail", "")
        base = "https://2ch.hk"
        image_url = (base + path) if path and path.startswith("/") else path
        thumb_url = (base + thumb) if thumb and thumb.startswith("/") else thumb
        return image_url or "", thumb_url or ""

    def _normalize_catalog_post(self, t, board):
        num = int(t.get("num", 0))
        image_url, thumb_url = self._image_urls(t)
        return {
            "post_id": num,
            "thread_id": num,
            "board": board,
            "site": self.site.domain,
            "subject": t.get("subject", ""),
            "comment": strip_html(t.get("comment", "")),
            "author": t.get("name", "Anonymous"),
            "timestamp": t.get("timestamp", 0),
            "reply_count": t.get("posts_count", 0),
            "image_count": t.get("files_count", 0),
            "is_op": 1,
            "is_pinned": 1 if t.get("sticky") else 0,
            "is_closed": 1 if t.get("closed") else 0,
            "fetched_at": _now_ts(),
            "image_url": image_url,
            "thumb_url": thumb_url,
        }

    def _normalize_post(self, p, board, thread_id, is_op=False):
        num = int(p.get("num", 0))
        image_url, thumb_url = self._image_urls(p)
        return {
            "post_id": num,
            "thread_id": thread_id,
            "board": board,
            "site": self.site.domain,
            "subject": p.get("subject", ""),
            "comment": strip_html(p.get("comment", "")),
            "author": p.get("name", "Anonymous"),
            "timestamp": p.get("timestamp", 0),
            "reply_count": 0,
            "image_count": len(p.get("files") or []),
            "is_op": 1 if is_op else 0,
            "is_pinned": 1 if p.get("sticky") else 0,
            "is_closed": 1 if p.get("closed") else 0,
            "fetched_at": _now_ts(),
            "image_url": image_url,
            "thumb_url": thumb_url,
        }

    def catalog_url(self, board):
        return self._url(self.site.catalog_path, board=board)

    def thread_url(self, board, thread_id):
        return self.site.thread_url.format(board=board, thread_id=thread_id)


class FoolFuukaAdapter:
    """Adapter for FoolFuuka archive APIs (desuarchive, 4plebs)."""

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )

    def _url(self, path, **kwargs):
        return self.site.api_base + path.format(**kwargs)

    def fetch_boards(self):
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def catalog_url(self, board):
        return None  # archives don't have catalogs

    def fetch_catalog(self, board):
        """FoolFuuka archives don't have catalogs — returns empty list."""
        return []

    def search(self, board, query, page=1):
        """Search archive via FoolFuuka API."""
        url = (f"{self.site.api_base}/_/api/chan/search/"
               f"?board={board}&text={quote(query)}&page={page}")
        data = self.fetcher.get_json(url)
        if data is None:
            return []
        # FoolFuuka returns {0: {posts: [...]}} or {error: ...}
        if isinstance(data, dict) and "error" in data:
            return []
        posts = []
        posts_data = data.get("0", data)
        if isinstance(posts_data, dict):
            posts_data = posts_data.get("posts", [])
        if isinstance(posts_data, list):
            for p in posts_data:
                posts.append(self._normalize_post(p, board))
        elif isinstance(posts_data, dict):
            for key, p in posts_data.items():
                if isinstance(p, dict):
                    posts.append(self._normalize_post(p, board))
        return posts

    def fetch_thread(self, board, thread_id):
        """Fetch archived thread."""
        url = self._url(self.site.thread_path, board=board,
                        thread_id=thread_id)
        data = self.fetcher.get_json(url)
        if data is None:
            return None
        # FoolFuuka thread response: {thread_id: {op: {...}, posts: {id: {...}}}}
        posts = []
        thread_data = data.get(str(thread_id), data)
        if isinstance(thread_data, dict):
            op = thread_data.get("op", {})
            if op:
                posts.append(self._normalize_post(op, board, is_op=True,
                                                  thread_id=thread_id))
            raw_posts = thread_data.get("posts", {})
            if isinstance(raw_posts, dict):
                for pid, p in sorted(raw_posts.items(),
                                     key=lambda x: int(x[0])):
                    posts.append(self._normalize_post(p, board,
                                                      thread_id=thread_id))
        return posts

    def _normalize_post(self, p, board, is_op=False, thread_id=None):
        pid = int(p.get("num", p.get("doc_id", 0)))
        tid = int(p.get("thread_num", thread_id or pid))
        ts = int(p.get("timestamp", 0))
        media = p.get("media")
        image_url = ""
        thumb_url = ""
        if media:
            image_url = media.get("media_link", "") or ""
            thumb_url = media.get("thumb_link", "") or ""
        return {
            "post_id": pid,
            "thread_id": tid,
            "board": board,
            "site": self.site.domain,
            "subject": p.get("title", "") or "",
            "comment": strip_html(p.get("comment_processed",
                                        p.get("comment", ""))),
            "author": p.get("name", "Anonymous"),
            "timestamp": ts,
            "reply_count": 0,
            "image_count": 1 if media else 0,
            "is_op": 1 if is_op or str(pid) == str(tid) else 0,
            "is_pinned": 0,
            "is_closed": 0,
            "fetched_at": _now_ts(),
            "image_url": image_url,
            "thumb_url": thumb_url,
        }

    def thread_url(self, board, thread_id):
        return self.site.thread_url.format(board=board, thread_id=thread_id)


class DatAdapter:
    """Adapter for 5ch dat-format boards.

    Uses bbsmenu to discover server→board mapping. Fetches subject.txt for
    catalogs and {key}.dat for threads. Encoding varies by site (cp932/utf-8).
    """

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        self._board_servers = None  # board→server map, lazy-loaded
        self._encoding = site_config.extra.get("encoding", "utf-8")
        self._extra_headers = {}
        if site_config.extra.get("user_agent"):
            self._extra_headers["User-Agent"] = site_config.extra["user_agent"]
        # Rate limit on multiple domains (servers vary)
        fetcher.set_rate_limit(site_config.domain, site_config.rate_limit)

    def _get_server(self, board):
        """Look up which server hosts a board (e.g., 'egg' for news4vip)."""
        if self._board_servers is None:
            self._board_servers = self._fetch_bbsmenu()
        return self._board_servers.get(board, board)

    def _fetch_bbsmenu(self):
        """Parse bbsmenu to build board→server map."""
        url = self.site.extra.get("bbsmenu_url", "")
        fmt = self.site.extra.get("bbsmenu_format", "html")
        mapping = {}

        if not url:
            return mapping

        try:
            if fmt == "json":
                data = self.fetcher.get_json(url, extra_headers=self._extra_headers)
                if data and isinstance(data, dict):
                    for category in data.get("menu_list", []):
                        for item in category.get("category_content", []):
                            board_url = item.get("url", "")
                            # https://egg.5ch.net/news4vip/ → server=egg, board=news4vip
                            m = re.match(r'https?://(\w+)\.\w+\.\w+/(\w+)/?', board_url)
                            if m:
                                mapping[m.group(2)] = m.group(1)
            else:
                text = self.fetcher.get_text(url, encoding=self._encoding,
                                             extra_headers=self._extra_headers)
                if text:
                    for m in re.finditer(
                        r'https?://(\w+)\.[^/]+/(\w+)/', text
                    ):
                        mapping[m.group(2)] = m.group(1)
        except Exception:
            pass  # fail gracefully — default boards still work with board as server

        return mapping

    def fetch_boards(self):
        if self._board_servers is None:
            self._board_servers = self._fetch_bbsmenu()
        if self._board_servers:
            return [{"board": b, "title": "", "pages": 0}
                    for b in sorted(self._board_servers.keys())]
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def fetch_catalog(self, board):
        from dat_parse import parse_subject_txt

        server = self._get_server(board)
        url = f"https://{server}.{self.site.domain}/{board}/subject.txt"

        # Set rate limit for this specific server domain
        self.fetcher.set_rate_limit(
            f"{server}.{self.site.domain}", self.site.rate_limit
        )

        try:
            text = self.fetcher.get_text(url, encoding=self._encoding,
                                         extra_headers=self._extra_headers)
        except Exception as e:
            # HTTP 451 (geo-block) or other errors
            if hasattr(e, 'response') and getattr(e.response, 'status_code', 0) == 451:
                raise RuntimeError(
                    f"HTTP 451: {self.site.domain} is geo-blocked from this IP"
                ) from e
            raise

        if text is None:
            return None

        threads = parse_subject_txt(text)
        now = _now_ts()
        posts = []
        for t in threads:
            key = int(t["key"])
            posts.append({
                "post_id": key,
                "thread_id": key,
                "board": board,
                "site": self.site.domain,
                "subject": t["title"],
                "comment": "",
                "author": "",
                "timestamp": key,  # dat key is unix timestamp
                "reply_count": t["count"],
                "image_count": 0,
                "is_op": 1,
                "is_pinned": 0,
                "is_closed": 0,
                "fetched_at": now,
            })
        return posts

    def fetch_thread(self, board, thread_id):
        from dat_parse import parse_dat_thread

        server = self._get_server(board)
        url = f"https://{server}.{self.site.domain}/{board}/dat/{thread_id}.dat"

        self.fetcher.set_rate_limit(
            f"{server}.{self.site.domain}", self.site.rate_limit
        )

        try:
            text = self.fetcher.get_text(url, encoding=self._encoding,
                                         extra_headers=self._extra_headers)
        except Exception as e:
            if hasattr(e, 'response') and getattr(e.response, 'status_code', 0) == 451:
                raise RuntimeError(
                    f"HTTP 451: {self.site.domain} is geo-blocked from this IP"
                ) from e
            raise

        if text is None:
            return None

        posts = parse_dat_thread(text, str(thread_id))
        for p in posts:
            p["board"] = board
            p["site"] = self.site.domain
        return posts

    def catalog_url(self, board):
        server = self._get_server(board)
        return f"https://{server}.{self.site.domain}/{board}/subject.txt"

    def thread_url(self, board, thread_id):
        server = self._get_server(board)
        return self.site.thread_url.format(
            server=server, board=board, thread_id=thread_id
        )


class ShitarabaAdapter:
    """Adapter for jbbs.shitaraba.net (Japanese hosted-board service).

    Boards use category/id format (e.g., 'computer/43680').
    EUC-JP encoding, <>-delimited fields.
    """

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        self._encoding = site_config.extra.get("encoding", "euc-jp")
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )

    def fetch_boards(self):
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def fetch_catalog(self, board):
        """Fetch thread list from subject.txt.

        Format: <key>.cgi,<title>(<count>)\n
        """
        url = f"{self.site.api_base}/{board}/subject.txt"
        text = self.fetcher.get_text(url, encoding=self._encoding)
        if text is None:
            return None

        now = _now_ts()
        posts = []
        for line in text.splitlines():
            line = line.strip()
            if not line:
                continue
            # 1234567890.cgi,Thread title(123)
            m = re.match(r'^(\d+)\.cgi,(.+)\((\d+)\)$', line)
            if m:
                key = int(m.group(1))
                posts.append({
                    "post_id": key,
                    "thread_id": key,
                    "board": board,
                    "site": self.site.domain,
                    "subject": m.group(2).strip(),
                    "comment": "",
                    "author": "",
                    "timestamp": key,
                    "reply_count": int(m.group(3)),
                    "image_count": 0,
                    "is_op": 1,
                    "is_pinned": 0,
                    "is_closed": 0,
                    "fetched_at": now,
                })
        return posts

    _JST = timezone(timedelta(hours=9))

    def _parse_shitaraba_date(self, date_str):
        """Parse Shitaraba date: 2024/01/15(土) 18:16:02 (JST)"""
        if not date_str:
            return 0
        date_str = re.sub(r'\([^)]*\)\s*', '', date_str).strip()
        try:
            dt = datetime.strptime(date_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=self._JST)
            return int(dt.timestamp())
        except ValueError:
            return 0

    def fetch_thread(self, board, thread_id):
        """Fetch thread from rawmode.cgi.

        Format: post_num<>name<>mail<>date<>body<>title<>ID
        """
        url = f"{self.site.api_base}/bbs/rawmode.cgi/{board}/{thread_id}/"
        text = self.fetcher.get_text(url, encoding=self._encoding)
        if text is None:
            return None

        now = _now_ts()
        posts = []
        for i, line in enumerate(text.splitlines()):
            line = line.strip()
            if not line:
                continue
            parts = line.split("<>")
            if len(parts) < 5:
                continue

            post_num = int(parts[0]) if parts[0].isdigit() else (i + 1)
            name = re.sub(r'<[^>]+>', '', parts[1]) if parts[1] else "名無し"
            date_str = parts[3]
            body = strip_dat_html(parts[4])
            title = parts[5] if len(parts) > 5 else ""

            posts.append({
                "post_id": int(thread_id) if i == 0 else int(thread_id) + post_num,
                "thread_id": int(thread_id),
                "board": board,
                "site": self.site.domain,
                "subject": title if i == 0 else "",
                "comment": body,
                "author": name,
                "timestamp": self._parse_shitaraba_date(date_str),
                "reply_count": 0,
                "image_count": 0,
                "is_op": 1 if i == 0 else 0,
                "is_pinned": 0,
                "is_closed": 0,
                "fetched_at": now,
            })
        return posts

    def catalog_url(self, board):
        return f"{self.site.api_base}/{board}/subject.txt"

    def thread_url(self, board, thread_id):
        return self.site.thread_url.format(board=board, thread_id=thread_id)


class MachiBBSAdapter:
    """Adapter for machi.to (Machi BBS — Japanese regional boards).

    Clean JSON API, UTF-8.
    """

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )

    def fetch_boards(self):
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def fetch_catalog(self, board):
        url = f"{self.site.api_base}/bbs/json.cgi/{board}/"
        data = self.fetcher.get_json(url)
        if data is None:
            return None

        now = _now_ts()
        posts = []
        for t in data.get("thread", []):
            key = int(t.get("key", 0))
            posts.append({
                "post_id": key,
                "thread_id": key,
                "board": board,
                "site": self.site.domain,
                "subject": t.get("subject", ""),
                "comment": "",
                "author": "",
                "timestamp": key,
                "reply_count": int(t.get("res", 0)),
                "image_count": 0,
                "is_op": 1,
                "is_pinned": 0,
                "is_closed": 0,
                "fetched_at": now,
            })
        return posts

    _JST = timezone(timedelta(hours=9))

    def _parse_machi_time(self, time_str):
        """Parse Machi BBS time field: '2025/09/27(土) 12:30:16 ID:LfHpXl0A' (JST)"""
        if not time_str:
            return 0
        # Strip ID suffix
        time_str = re.sub(r'\s+ID:\S+', '', time_str).strip()
        # Strip day-of-week
        time_str = re.sub(r'\([^)]*\)\s*', '', time_str).strip()
        try:
            dt = datetime.strptime(time_str, "%Y/%m/%d %H:%M:%S").replace(tzinfo=self._JST)
            return int(dt.timestamp())
        except ValueError:
            return 0

    def fetch_thread(self, board, thread_id):
        url = f"{self.site.api_base}/bbs/json.cgi/{board}/{thread_id}/"
        data = self.fetcher.get_json(url)
        if data is None:
            return None

        now = _now_ts()
        posts = []
        for i, p in enumerate(data.get("log", [])):
            post_no = int(p.get("no", i + 1))
            ts = self._parse_machi_time(p.get("time", ""))
            posts.append({
                "post_id": int(thread_id) if i == 0 else int(thread_id) + post_no,
                "thread_id": int(thread_id),
                "board": board,
                "site": self.site.domain,
                "subject": p.get("subject", "") if i == 0 else "",
                "comment": strip_html(p.get("message", "")),
                "author": p.get("name", "名無し"),
                "timestamp": ts,
                "reply_count": 0,
                "image_count": 0,
                "is_op": 1 if i == 0 else 0,
                "is_pinned": 0,
                "is_closed": 0,
                "fetched_at": now,
            })
        return posts

    def catalog_url(self, board):
        return f"{self.site.api_base}/bbs/json.cgi/{board}/"

    def thread_url(self, board, thread_id):
        return self.site.thread_url.format(board=board, thread_id=thread_id)


class DCInsideAdapter:
    """Adapter for dcinside.com (Korean imageboard).

    Scrapes HTML from gall.dcinside.com web interface.
    Uses mgallery paths for minor galleries (where most discussion happens).
    """

    _KST = timezone(timedelta(hours=9))

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        self._extra_headers = {
            "User-Agent": site_config.extra.get(
                "user_agent",
                "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                "(KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36",
            ),
            "Accept-Language": "ko-KR,ko;q=0.9",
            "Referer": "https://gall.dcinside.com/",
        }
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )
        self._gallery_type = {}  # board → "mgallery/board" | "board" | "mini/board"

    def fetch_boards(self):
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def _resolve_gallery_type(self, board):
        """Detect gallery type for a board (major/minor/mini).

        DCInside has 3 gallery types with different URL prefixes:
        - Major galleries: /board/
        - Minor galleries: /mgallery/board/
        - Mini galleries: /mini/board/
        """
        if board in self._gallery_type:
            return self._gallery_type[board]

        # Try each type, return first that works (has post rows)
        for gtype in ("mgallery/board", "board", "mini/board"):
            url = f"{self.site.api_base}/{gtype}/lists/?id={board}&page=1"
            try:
                resp = self.fetcher.get(url, max_retries=1,
                                        extra_headers=self._extra_headers)
                if resp and resp.status_code == 200 and len(resp.text) > 500:
                    self._gallery_type[board] = gtype
                    return gtype
            except Exception:
                continue

        # Default to mgallery
        self._gallery_type[board] = "mgallery/board"
        return "mgallery/board"

    def _parse_dc_date(self, date_str):
        """Parse DCInside date string to unix timestamp.

        Formats: '2024-01-15 12:30:00', '2024.01.15', '01.15', '12:30:00'
        """
        if not date_str:
            return 0
        date_str = date_str.strip()
        for fmt in ("%Y-%m-%d %H:%M:%S", "%Y.%m.%d %H:%M:%S",
                     "%Y-%m-%d", "%Y.%m.%d"):
            try:
                dt = datetime.strptime(date_str, fmt).replace(tzinfo=self._KST)
                return int(dt.timestamp())
            except ValueError:
                continue
        return 0

    def fetch_catalog(self, board):
        """Fetch catalog by scraping HTML table from gallery list page."""
        gtype = self._resolve_gallery_type(board)
        url = f"{self.site.api_base}/{gtype}/lists/?id={board}&page=1"
        resp = self.fetcher.get(url, extra_headers=self._extra_headers)
        if resp is None:
            return None
        text = resp.text

        now = _now_ts()
        posts = []

        # Extract table rows with attributes: <tr class="ub-content us-post" data-no="..." data-type="...">...</tr>
        rows = re.findall(
            r'<tr\s+class="ub-content\s+us-post"\s+'
            r'data-no="(\d+)"\s+data-type="([^"]*)"[^>]*>(.*?)</tr>',
            text, re.DOTALL
        )
        for data_no, data_type, row in rows:
            no = int(data_no)
            is_pinned = 1 if data_type == "icon_notice" else 0

            # Title (inside <a> tag within gall_tit; class may be "gall_tit ub-word")
            m_tit = re.search(
                r'<td\s+class="gall_tit[^"]*"[^>]*>.*?<a[^>]*>\s*(.*?)\s*</a>',
                row, re.DOTALL
            )
            title = ""
            if m_tit:
                title = re.sub(r'<[^>]+>', '', m_tit.group(1)).strip()

            # Author
            m_writer = re.search(
                r'<td\s+class="gall_writer"[^>]*'
                r'(?:\s+data-nick="([^"]*)")?[^>]*>',
                row
            )
            author = ""
            if m_writer and m_writer.group(1):
                author = m_writer.group(1)
            elif m_writer:
                # Fallback: extract text from inside the td
                m_writer_inner = re.search(
                    r'<td\s+class="gall_writer"[^>]*>(.*?)</td>',
                    row, re.DOTALL
                )
                if m_writer_inner:
                    author = re.sub(r'<[^>]+>', '', m_writer_inner.group(1)).strip()

            # Date
            m_date = re.search(
                r'<td\s+class="gall_date"[^>]*'
                r'(?:\s+title="([^"]*)")?[^>]*>(.*?)</td>',
                row, re.DOTALL
            )
            ts = 0
            if m_date:
                # Prefer title attr (full datetime), fallback to inner text
                date_str = m_date.group(1) or re.sub(r'<[^>]+>', '', m_date.group(2)).strip()
                ts = self._parse_dc_date(date_str)

            # Reply count from [N] in reply_numbox
            m_reply = re.search(
                r'<span\s+class="reply_num"[^>]*>\[(\d+)\]</span>', row
            )
            reply_count = int(m_reply.group(1)) if m_reply else 0

            posts.append({
                "post_id": no,
                "thread_id": no,
                "board": board,
                "site": self.site.domain,
                "subject": title,
                "comment": "",
                "author": author,
                "timestamp": ts,
                "reply_count": reply_count,
                "image_count": 0,
                "is_op": 1,
                "is_pinned": is_pinned,
                "is_closed": 0,
                "fetched_at": now,
            })

        return posts

    def fetch_thread(self, board, thread_id):
        """Fetch thread by scraping HTML from view page."""
        gtype = self._resolve_gallery_type(board)
        url = f"{self.site.api_base}/{gtype}/view/?id={board}&no={thread_id}"
        resp = self.fetcher.get(url, extra_headers=self._extra_headers)
        if resp is None:
            return None
        text = resp.text

        now = _now_ts()
        posts = []

        # Extract OP subject from title area
        m_subj = re.search(
            r'<span\s+class="title_subject"[^>]*>(.*?)</span>',
            text, re.DOTALL
        )
        subject = re.sub(r'<[^>]+>', '', m_subj.group(1)).strip() if m_subj else ""

        # Extract OP author from data-nick attribute
        m_author = re.search(
            r'class="gall_writer[^"]*"[^>]*data-nick="([^"]*)"',
            text
        )
        author = m_author.group(1) if m_author else ""

        # Extract date from title attribute
        m_date = re.search(r'class="gall_date"[^>]*title="([^"]*)"', text)
        ts = 0
        if m_date:
            ts = self._parse_dc_date(m_date.group(1))

        # Extract OP body from write_div (may contain nested divs).
        # Greedy match up to the last </div> before <script id="img_numbering
        m_body = re.search(
            r'<div\s+class="write_div"[^>]*>(.*)</div>\s*<script\s+id="img_numbering',
            text, re.DOTALL
        )
        if not m_body:
            # Fallback: greedy up to </div> before any <script
            m_body = re.search(
                r'<div\s+class="write_div"[^>]*>(.*)</div>\s*<script',
                text, re.DOTALL
            )
        body = ""
        if m_body:
            body = strip_dcinside_html(m_body.group(1))

        # Reply count from page
        m_reply = re.search(r'class="gall_comment"\s*>\s*[\[(\s]*(\d+)', text)
        reply_count = int(m_reply.group(1)) if m_reply else 0

        posts.append({
            "post_id": int(thread_id),
            "thread_id": int(thread_id),
            "board": board,
            "site": self.site.domain,
            "subject": subject,
            "comment": body,
            "author": author,
            "timestamp": ts,
            "reply_count": reply_count,
            "image_count": 0,
            "is_op": 1,
            "is_pinned": 0,
            "is_closed": 0,
            "fetched_at": now,
        })

        # Comments are loaded client-side via JS; no server-rendered comment
        # section or accessible AJAX endpoint without browser cookies/tokens.
        # OP content is still useful for search/ingestion.

        return posts

    def catalog_url(self, board):
        gtype = self._resolve_gallery_type(board)
        return f"{self.site.api_base}/{gtype}/lists/?id={board}&page=1"

    def thread_url(self, board, thread_id):
        gtype = self._resolve_gallery_type(board)
        return f"{self.site.api_base}/{gtype}/view/?id={board}&no={thread_id}"


class ArcaLiveAdapter:
    """Adapter for arca.live (Korean community platform).

    Uses mobile JSON API with Android app User-Agent.
    """

    _KST = timezone(timedelta(hours=9))

    def __init__(self, site_config, fetcher):
        self.site = site_config
        self.fetcher = fetcher
        self._extra_headers = {
            "User-Agent": site_config.extra.get(
                "user_agent", "net.umanle.arca.android.playstore/0.9.75"
            ),
            "X-Device-Token": self._gen_device_token(),
        }
        fetcher.set_rate_limit(
            site_config.api_base.split("/")[2], site_config.rate_limit
        )

    @staticmethod
    def _gen_device_token():
        import random
        return random.getrandbits(256).to_bytes(32, "big").hex()

    def fetch_boards(self):
        return [{"board": b, "title": "", "pages": 0}
                for b in self.site.default_boards]

    def _parse_arca_date(self, date_str):
        """Parse arca.live date string to unix timestamp.

        Formats: '2024-01-15T12:30:00+09:00', '2024-01-15T12:30:00.000Z'
        """
        if not date_str:
            return 0
        try:
            raw = str(date_str).replace("Z", "+00:00")
            dt = datetime.fromisoformat(raw)
            return int(dt.timestamp())
        except (ValueError, TypeError):
            return 0

    def fetch_catalog(self, board):
        """Fetch article list from mobile JSON API."""
        url = f"{self.site.api_base}/api/app/list/channel/{board}"
        data = self.fetcher.get_json(url, extra_headers=self._extra_headers)
        if data is None:
            return None

        now = _now_ts()
        posts = []
        articles = data.get("articles", data) if isinstance(data, dict) else data
        if not isinstance(articles, list):
            articles = []
        for a in articles:
            aid = int(a.get("id", 0))
            if not aid:
                continue
            ts = self._parse_arca_date(a.get("createdAt", a.get("created_at", "")))
            # Author may be nested object or string
            author_raw = a.get("author", "")
            if isinstance(author_raw, dict):
                author = author_raw.get("nickname", author_raw.get("nick", ""))
            else:
                author = str(author_raw)

            posts.append({
                "post_id": aid,
                "thread_id": aid,
                "board": a.get("boardSlug", a.get("channel", board)),
                "site": self.site.domain,
                "subject": a.get("title", a.get("subject", "")),
                "comment": strip_html(a.get("content", "")),
                "author": author,
                "timestamp": ts,
                "reply_count": int(a.get("commentCount", a.get("comment_count", 0))),
                "image_count": 0,
                "is_op": 1,
                "is_pinned": 1 if a.get("isNotice") or a.get("is_notice") else 0,
                "is_closed": 0,
                "fetched_at": now,
            })
        return posts

    def fetch_thread(self, board, thread_id):
        """Fetch single article from mobile JSON API."""
        url = f"{self.site.api_base}/api/app/view/article/breaking/{thread_id}"
        data = self.fetcher.get_json(url, extra_headers=self._extra_headers)
        if data is None:
            return None

        now = _now_ts()
        posts = []

        a = data
        aid = int(a.get("id", thread_id))
        ts = self._parse_arca_date(a.get("createdAt", a.get("created_at", "")))
        author_raw = a.get("author", "")
        if isinstance(author_raw, dict):
            author = author_raw.get("nickname", author_raw.get("nick", ""))
        else:
            author = str(author_raw)

        posts.append({
            "post_id": aid,
            "thread_id": aid,
            "board": a.get("boardSlug", a.get("channel", board)),
            "site": self.site.domain,
            "subject": a.get("title", a.get("subject", "")),
            "comment": strip_html(a.get("content", "")),
            "author": author,
            "timestamp": ts,
            "reply_count": int(a.get("commentCount", a.get("comment_count", 0))),
            "image_count": 0,
            "is_op": 1,
            "is_pinned": 0,
            "is_closed": 0,
            "fetched_at": now,
        })

        # Extract comments if present in response
        comments = a.get("comments", [])
        if isinstance(comments, list):
            for c in comments:
                cid = int(c.get("id", 0))
                if not cid:
                    continue
                cts = self._parse_arca_date(c.get("createdAt", c.get("created_at", "")))
                c_author_raw = c.get("author", "")
                if isinstance(c_author_raw, dict):
                    c_author = c_author_raw.get("nickname", c_author_raw.get("nick", ""))
                else:
                    c_author = str(c_author_raw)
                posts.append({
                    "post_id": cid,
                    "thread_id": aid,
                    "board": board,
                    "site": self.site.domain,
                    "subject": "",
                    "comment": strip_html(c.get("content", "")),
                    "author": c_author,
                    "timestamp": cts,
                    "reply_count": 0,
                    "image_count": 0,
                    "is_op": 0,
                    "is_pinned": 0,
                    "is_closed": 0,
                    "fetched_at": now,
                })

        return posts

    def catalog_url(self, board):
        return f"{self.site.api_base}/api/app/list/channel/{board}"

    def thread_url(self, board, thread_id):
        return self.site.thread_url.format(board=board, thread_id=thread_id)


# ── Factory ───────────────────────────────────────────────────────────

_ADAPTERS = {
    "vichan": VichanAdapter,
    "lynxchan": LynxchanAdapter,
    "jschan": JschanAdapter,
    "makaba": MakabaAdapter,
    "foolfuuka": FoolFuukaAdapter,
    "dat": DatAdapter,
    "shitaraba": ShitarabaAdapter,
    "machibbs": MachiBBSAdapter,
    "dcinside": DCInsideAdapter,
    "arcalive": ArcaLiveAdapter,
}


def get_adapter(site_domain, fetcher):
    """Create the right adapter for a site domain.

    Args:
        site_domain: Domain string like '4chan.org'
        fetcher: Fetcher instance

    Returns:
        EngineAdapter instance

    Raises:
        KeyError: if site not in registry
    """
    config = SITES[site_domain]
    cls = _ADAPTERS[config.engine]
    return cls(config, fetcher)
