"""SQLite + FTS5 storage for imageboard posts."""

import sqlite3
import time
from pathlib import Path

DEFAULT_DB_PATH = Path.home() / ".claude" / "cache" / "chans.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS posts (
    site        TEXT NOT NULL,
    board       TEXT NOT NULL,
    post_id     INTEGER NOT NULL,
    thread_id   INTEGER NOT NULL,
    subject     TEXT DEFAULT '',
    comment     TEXT DEFAULT '',
    author      TEXT DEFAULT 'Anonymous',
    timestamp   INTEGER DEFAULT 0,
    reply_count INTEGER DEFAULT 0,
    image_count INTEGER DEFAULT 0,
    is_op       INTEGER DEFAULT 0,
    is_pinned   INTEGER DEFAULT 0,
    is_closed   INTEGER DEFAULT 0,
    fetched_at  INTEGER NOT NULL,
    image_url   TEXT DEFAULT '',
    thumb_url   TEXT DEFAULT '',
    PRIMARY KEY (site, board, thread_id, post_id)
);

CREATE INDEX IF NOT EXISTS idx_posts_thread
    ON posts (site, board, thread_id);
CREATE INDEX IF NOT EXISTS idx_posts_timestamp
    ON posts (timestamp DESC);
CREATE INDEX IF NOT EXISTS idx_posts_site_board
    ON posts (site, board);

CREATE VIRTUAL TABLE IF NOT EXISTS posts_fts USING fts5(
    subject, comment, author, site, board,
    content='posts',
    content_rowid='rowid',
    tokenize='trigram'
);

-- Triggers to keep FTS in sync
CREATE TRIGGER IF NOT EXISTS posts_ai AFTER INSERT ON posts BEGIN
    INSERT INTO posts_fts(rowid, subject, comment, author, site, board)
    VALUES (new.rowid, new.subject, new.comment, new.author, new.site, new.board);
END;

CREATE TRIGGER IF NOT EXISTS posts_ad AFTER DELETE ON posts BEGIN
    INSERT INTO posts_fts(posts_fts, rowid, subject, comment, author, site, board)
    VALUES ('delete', old.rowid, old.subject, old.comment, old.author, old.site, old.board);
END;

CREATE TRIGGER IF NOT EXISTS posts_au AFTER UPDATE ON posts BEGIN
    INSERT INTO posts_fts(posts_fts, rowid, subject, comment, author, site, board)
    VALUES ('delete', old.rowid, old.subject, old.comment, old.author, old.site, old.board);
    INSERT INTO posts_fts(rowid, subject, comment, author, site, board)
    VALUES (new.rowid, new.subject, new.comment, new.author, new.site, new.board);
END;

CREATE TABLE IF NOT EXISTS fetch_state (
    site          TEXT NOT NULL,
    board         TEXT NOT NULL,
    last_modified TEXT DEFAULT '',
    last_fetched  INTEGER DEFAULT 0,
    PRIMARY KEY (site, board)
);
"""


class ChansDB:
    """SQLite database for imageboard posts with FTS5 search."""

    def __init__(self, db_path=None):
        self.db_path = Path(db_path) if db_path else DEFAULT_DB_PATH
        self.db_path.parent.mkdir(parents=True, exist_ok=True)
        self.conn = sqlite3.connect(str(self.db_path))
        self.conn.row_factory = sqlite3.Row
        self.conn.execute("PRAGMA journal_mode=WAL")
        self.conn.execute("PRAGMA synchronous=NORMAL")
        needs_fts_rebuild = self._migrate_pk()
        if not needs_fts_rebuild:
            needs_fts_rebuild = self._migrate_fts_tokenizer()
        self.conn.executescript(SCHEMA)
        self._migrate_add_image_cols()
        if needs_fts_rebuild:
            self._rebuild_fts()

    def _migrate_pk(self):
        """Rebuild posts table if PK is missing thread_id (old schema).

        Returns True if FTS needs rebuilding after SCHEMA runs.
        """
        row = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='posts'"
        ).fetchone()
        if not row or not row[0]:
            return False  # table doesn't exist yet, SCHEMA will create it
        create_sql = row[0]
        # Old PK: PRIMARY KEY (site, board, post_id)
        # New PK: PRIMARY KEY (site, board, thread_id, post_id)
        pk_part = create_sql.split("PRIMARY KEY")[-1] if "PRIMARY KEY" in create_sql else ""
        if "thread_id" in pk_part:
            return False  # already migrated
        # Drop dependent objects
        self.conn.executescript("""
            DROP TRIGGER IF EXISTS posts_ai;
            DROP TRIGGER IF EXISTS posts_ad;
            DROP TRIGGER IF EXISTS posts_au;
            DROP TABLE IF EXISTS posts_fts;
            DROP INDEX IF EXISTS idx_posts_thread;
            DROP INDEX IF EXISTS idx_posts_timestamp;
            DROP INDEX IF EXISTS idx_posts_site_board;
        """)
        # Rebuild table with new PK (includes image columns)
        self.conn.execute("""
            CREATE TABLE posts_new (
                site        TEXT NOT NULL,
                board       TEXT NOT NULL,
                post_id     INTEGER NOT NULL,
                thread_id   INTEGER NOT NULL,
                subject     TEXT DEFAULT '',
                comment     TEXT DEFAULT '',
                author      TEXT DEFAULT 'Anonymous',
                timestamp   INTEGER DEFAULT 0,
                reply_count INTEGER DEFAULT 0,
                image_count INTEGER DEFAULT 0,
                is_op       INTEGER DEFAULT 0,
                is_pinned   INTEGER DEFAULT 0,
                is_closed   INTEGER DEFAULT 0,
                fetched_at  INTEGER NOT NULL,
                image_url   TEXT DEFAULT '',
                thumb_url   TEXT DEFAULT '',
                PRIMARY KEY (site, board, thread_id, post_id)
            )
        """)
        self.conn.execute("""
            INSERT OR IGNORE INTO posts_new (
                site, board, post_id, thread_id, subject, comment,
                author, timestamp, reply_count, image_count,
                is_op, is_pinned, is_closed, fetched_at
            )
            SELECT site, board, post_id, thread_id, subject, comment,
                   author, timestamp, reply_count, image_count,
                   is_op, is_pinned, is_closed, fetched_at
            FROM posts
        """)
        self.conn.execute("DROP TABLE posts")
        self.conn.execute("ALTER TABLE posts_new RENAME TO posts")
        self.conn.commit()
        return True  # SCHEMA will create FTS, then _rebuild_fts populates it

    def _migrate_fts_tokenizer(self):
        """Rebuild FTS table if it uses the old porter tokenizer (no CJK support).

        Returns True if FTS needs rebuilding after SCHEMA runs.
        """
        row = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE name = 'posts_fts'"
        ).fetchone()
        if row and row[0] and 'porter' in row[0]:
            self.conn.executescript("""
                DROP TRIGGER IF EXISTS posts_ai;
                DROP TRIGGER IF EXISTS posts_ad;
                DROP TRIGGER IF EXISTS posts_au;
                DROP TABLE IF EXISTS posts_fts;
            """)
            return True  # SCHEMA will create FTS, then _rebuild_fts populates it
        return False

    def _migrate_add_image_cols(self):
        """Add image_url and thumb_url columns to existing posts table."""
        row = self.conn.execute(
            "SELECT sql FROM sqlite_master WHERE type='table' AND name='posts'"
        ).fetchone()
        if not row or not row[0]:
            return
        if "image_url" in row[0]:
            return  # already has image columns
        self.conn.execute(
            "ALTER TABLE posts ADD COLUMN image_url TEXT DEFAULT ''"
        )
        self.conn.execute(
            "ALTER TABLE posts ADD COLUMN thumb_url TEXT DEFAULT ''"
        )
        self.conn.commit()

    def _rebuild_fts(self):
        """Repopulate FTS index from existing posts."""
        self.conn.execute("""
            INSERT INTO posts_fts(rowid, subject, comment, author, site, board)
            SELECT rowid, subject, comment, author, site, board FROM posts
        """)
        self.conn.commit()

    def close(self):
        self.conn.close()

    def upsert_posts(self, posts):
        """Insert or update a batch of posts (list of dicts).

        On conflict, prefers non-empty values for text fields so that
        catalog stubs (empty comment/author) don't overwrite richer
        thread data fetched later (or earlier).
        """
        if not posts:
            return 0
        # Ensure image fields exist (adapters without image support)
        for p in posts:
            p.setdefault("image_url", "")
            p.setdefault("thumb_url", "")
        sql = """
            INSERT INTO posts (
                site, board, post_id, thread_id, subject, comment,
                author, timestamp, reply_count, image_count,
                is_op, is_pinned, is_closed, fetched_at,
                image_url, thumb_url
            ) VALUES (
                :site, :board, :post_id, :thread_id, :subject, :comment,
                :author, :timestamp, :reply_count, :image_count,
                :is_op, :is_pinned, :is_closed, :fetched_at,
                :image_url, :thumb_url
            )
            ON CONFLICT(site, board, thread_id, post_id) DO UPDATE SET
                subject = CASE WHEN excluded.subject != ''
                               THEN excluded.subject ELSE posts.subject END,
                comment = CASE WHEN excluded.comment != ''
                               THEN excluded.comment ELSE posts.comment END,
                author = CASE WHEN excluded.author != '' AND excluded.author != 'Anonymous'
                              THEN excluded.author ELSE posts.author END,
                timestamp = CASE WHEN excluded.timestamp > 0
                                 THEN excluded.timestamp ELSE posts.timestamp END,
                reply_count = CASE WHEN excluded.reply_count > 0
                                  THEN excluded.reply_count ELSE posts.reply_count END,
                image_count = CASE WHEN excluded.image_count > 0
                                  THEN excluded.image_count ELSE posts.image_count END,
                image_url = CASE WHEN excluded.image_url != ''
                                 THEN excluded.image_url ELSE posts.image_url END,
                thumb_url = CASE WHEN excluded.thumb_url != ''
                                 THEN excluded.thumb_url ELSE posts.thumb_url END,
                is_pinned = excluded.is_pinned,
                is_closed = excluded.is_closed,
                fetched_at = excluded.fetched_at
        """
        with self.conn:
            self.conn.executemany(sql, posts)
        return len(posts)

    def search(self, query, site=None, board=None, limit=50):
        """FTS5 search across posts. Returns list of Row objects.

        Uses trigram FTS5 when all terms are 3+ chars (trigram minimum).
        Falls back to LIKE when any term is shorter (e.g., 'ai', '東京').
        """
        params = {"limit": limit}
        terms = query.split()

        # Trigram FTS needs every term to be >= 3 chars
        if not terms or any(len(t) < 3 for t in terms):
            return self._search_like(query, site, board, params)

        # Quote each term individually for literal matching + implicit AND
        safe_query = " ".join('"' + t.replace('"', '""') + '"' for t in terms)
        params["query"] = safe_query
        clauses = ["posts_fts MATCH :query"]
        if site:
            clauses.append("p.site = :site")
            params["site"] = site
        if board:
            clauses.append("p.board = :board")
            params["board"] = board
        where = " AND ".join(clauses)
        sql = f"""
            SELECT p.*, rank
            FROM posts p
            JOIN posts_fts ON posts_fts.rowid = p.rowid
            WHERE {where}
            ORDER BY rank
            LIMIT :limit
        """
        try:
            return self.conn.execute(sql, params).fetchall()
        except sqlite3.OperationalError:
            # FTS parse error — fall back to LIKE
            params = {"limit": limit}
            return self._search_like(query, site, board, params)

    def _search_like(self, query, site, board, params):
        """LIKE fallback for short queries or FTS errors.

        ANDs a separate LIKE per term so 'ai ml' matches posts
        containing both 'ai' and 'ml' in any order.
        """
        terms = query.split()
        if not terms:
            return []
        clauses = []
        for i, term in enumerate(terms):
            key = f"p{i}"
            params[key] = f"%{term}%"
            clauses.append(f"(p.subject LIKE :{key} OR p.comment LIKE :{key})")
        if site:
            clauses.append("p.site = :site")
            params["site"] = site
        if board:
            clauses.append("p.board = :board")
            params["board"] = board
        where = " AND ".join(clauses)
        sql = f"""
            SELECT p.*, 0 as rank
            FROM posts p
            WHERE {where}
            ORDER BY p.timestamp DESC
            LIMIT :limit
        """
        return self.conn.execute(sql, params).fetchall()

    def get_thread(self, site, board, thread_id):
        """Get all posts in a thread, ordered by post_id."""
        sql = """
            SELECT * FROM posts
            WHERE site = ? AND board = ? AND thread_id = ?
            ORDER BY post_id
        """
        return self.conn.execute(sql, (site, board, thread_id)).fetchall()

    def get_catalog(self, site, board, limit=200):
        """Get OP posts for a site/board, ordered by most recent."""
        sql = """
            SELECT * FROM posts
            WHERE site = ? AND board = ? AND is_op = 1
            ORDER BY timestamp DESC
            LIMIT ?
        """
        return self.conn.execute(sql, (site, board, limit)).fetchall()

    def get_stats(self):
        """Get post counts per site/board."""
        sql = """
            SELECT site, board,
                   COUNT(*) as total_posts,
                   SUM(is_op) as threads,
                   MAX(fetched_at) as last_fetched
            FROM posts
            GROUP BY site, board
            ORDER BY site, board
        """
        return self.conn.execute(sql).fetchall()

    def update_fetch_state(self, site, board, last_modified=""):
        """Update the fetch state for a site/board."""
        sql = """
            INSERT INTO fetch_state (site, board, last_modified, last_fetched)
            VALUES (?, ?, ?, ?)
            ON CONFLICT(site, board) DO UPDATE SET
                last_modified = excluded.last_modified,
                last_fetched = excluded.last_fetched
        """
        with self.conn:
            self.conn.execute(sql, (site, board, last_modified, int(time.time())))

    def get_fetch_state(self, site, board):
        """Get the fetch state for a site/board."""
        sql = "SELECT * FROM fetch_state WHERE site = ? AND board = ?"
        return self.conn.execute(sql, (site, board)).fetchone()
