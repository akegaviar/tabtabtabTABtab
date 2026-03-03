"""Parser for 5ch dat format — shared by DatAdapter."""

import re
import time
from datetime import datetime, timezone, timedelta

from html_strip import strip_dat_html

_JST = timezone(timedelta(hours=9))


def parse_subject_txt(text):
    """Parse subject.txt thread listing.

    Format: <key>.dat<><title> (<count>)\n

    Returns list of dicts: {key, title, count}
    """
    threads = []
    for line in text.splitlines():
        line = line.strip()
        if not line:
            continue
        # 1234567890.dat<>Thread title here (123)
        m = re.match(r'^(\d+)\.dat<>(.+)\s+\((\d+)\)$', line)
        if m:
            threads.append({
                "key": m.group(1),
                "title": m.group(2),
                "count": int(m.group(3)),
            })
    return threads


def _parse_dat_date(date_str):
    """Parse 5ch-style date string to unix timestamp.

    Formats:
      2024/01/15(月) 12:30:00.00 ID:AbCdEfGh0
      2024/01/15(月) 12:30:00
      2024/01/15 12:30:00
    """
    if not date_str:
        return 0
    # Strip trailing ID
    date_str = re.sub(r'\s+ID:\S+', '', date_str).strip()
    # Strip day-of-week in parens
    date_str = re.sub(r'\([^)]*\)\s*', '', date_str).strip()
    # Strip fractional seconds
    date_str = re.sub(r'\.\d+$', '', date_str).strip()

    for fmt in ("%Y/%m/%d %H:%M:%S", "%Y/%m/%d %H:%M"):
        try:
            dt = datetime.strptime(date_str, fmt).replace(tzinfo=_JST)
            return int(dt.timestamp())
        except ValueError:
            continue
    return 0


def parse_dat_thread(text, thread_key):
    """Parse a dat-format thread file.

    Format per line: name<>mail<>date_id<>body<>title
    (title only on first line)

    Returns list of normalized 14-key post dicts.
    """
    posts = []
    thread_id = int(thread_key)
    now = int(time.time())

    for i, line in enumerate(text.splitlines()):
        line = line.strip()
        if not line:
            continue
        parts = line.split("<>")
        if len(parts) < 4:
            continue

        name = parts[0] or "名無し"
        # parts[1] = mail (sage, etc.) — skip
        date_str = parts[2]
        body = parts[3] if len(parts) > 3 else ""
        title = parts[4] if len(parts) > 4 else ""

        ts = _parse_dat_date(date_str)
        post_num = i + 1

        posts.append({
            "post_id": thread_id if i == 0 else thread_id + post_num,
            "thread_id": thread_id,
            "board": "",  # filled by adapter
            "site": "",   # filled by adapter
            "subject": title if i == 0 else "",
            "comment": strip_dat_html(body),
            "author": re.sub(r'<[^>]+>', '', name),  # strip HTML from name
            "timestamp": ts if ts else thread_id,
            "reply_count": 0,
            "image_count": 0,
            "is_op": 1 if i == 0 else 0,
            "is_pinned": 0,
            "is_closed": 0,
            "fetched_at": now,
        })

    return posts
