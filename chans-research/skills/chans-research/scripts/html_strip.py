"""HTML→plaintext conversion for imageboard post markup."""

import html
import re
from html.parser import HTMLParser


def strip_html(text):
    """Strip HTML tags and decode entities from imageboard post HTML.

    Handles vichan/4chan markup: <br>, <wbr>, quotelinks, greentext, spoilers.
    """
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'<wbr\s*/?>', '', text)
    # Quote links: >>12345
    text = re.sub(r'<a href="#p(\d+)"[^>]*>&gt;&gt;(\d+)</a>', r'>>\2', text)
    # Cross-board links: >>>/g/12345
    text = re.sub(r'<a[^>]*class="quotelink"[^>]*>&gt;&gt;&gt;(/[^<]+)</a>', r'>>>\1', text)
    # Greentext
    text = re.sub(r'<span class="quote">&gt;(.*?)</span>', r'>\1', text)
    # Spoiler text
    text = re.sub(r'<s>(.*?)</s>', r'[spoiler]\1[/spoiler]', text, flags=re.DOTALL)
    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text)


def strip_lynxchan_html(text):
    """Strip LynxChan-style HTML (uses <p>, <br>, different classes)."""
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text)
    text = re.sub(r'</p>\s*<p>', '\n\n', text)
    text = re.sub(r'</?p>', '', text)
    # Greentext
    text = re.sub(r'<span class="greenText">&gt;(.*?)</span>', r'>\1', text)
    # Quote links
    text = re.sub(r'<a[^>]*class="quoteLink"[^>]*>&gt;&gt;(\d+)</a>', r'>>\1', text)
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text)


def strip_dat_html(text):
    """Strip HTML from 5ch dat-format post bodies.

    Handles <br>, <a href>, <b>, sssp:// icon refs, and HTML entities.
    """
    if not text:
        return ""
    text = re.sub(r'<br\s*/?>', '\n', text)
    # Anchor links (quote refs like >>123)
    text = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', text)
    # Bold
    text = re.sub(r'</?b>', '', text)
    # sssp:// icon references
    text = re.sub(r'sssp://[^\s<]+', '', text)
    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    return html.unescape(text).strip()


def strip_dcinside_html(text):
    """Strip HTML from DCInside web page post bodies.

    Handles <br>, <p>, embedded link previews (og-div), dcimg images,
    and standard entity decoding.
    """
    if not text:
        return ""
    # Embedded link previews
    text = re.sub(r'<div class="og-div"[^>]*>.*?</div>', '', text, flags=re.DOTALL)
    # Image tags → strip
    text = re.sub(r'<img[^>]*>', '', text)
    # <br> → newline
    text = re.sub(r'<br\s*/?>', '\n', text)
    # <p> handling
    text = re.sub(r'</p>\s*<p[^>]*>', '\n\n', text)
    text = re.sub(r'</?p[^>]*>', '', text)
    # <div> → newline
    text = re.sub(r'</div>\s*<div[^>]*>', '\n', text)
    text = re.sub(r'</?div[^>]*>', '', text)
    # Anchor links (keep text)
    text = re.sub(r'<a[^>]*>([^<]*)</a>', r'\1', text)
    # Strip remaining tags
    text = re.sub(r'<[^>]+>', '', text)
    # Collapse excessive newlines
    text = re.sub(r'\n{3,}', '\n\n', text)
    return html.unescape(text).strip()
