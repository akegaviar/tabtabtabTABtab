"""HTTP fetch layer with per-domain rate limits, If-Modified-Since, and retries."""

import time

import requests

USER_AGENT = "chans-research/2.0"


class Fetcher:
    """HTTP client with per-domain rate limiting and conditional requests."""

    def __init__(self, timeout=15):
        self.timeout = timeout
        self.session = requests.Session()
        self.session.headers["User-Agent"] = USER_AGENT
        self._last_request = {}  # domain → timestamp
        self._last_modified = {}  # url → Last-Modified header value
        self._rate_limits = {}  # domain → min seconds between requests

    def set_rate_limit(self, domain, seconds):
        """Set per-domain rate limit in seconds."""
        self._rate_limits[domain] = seconds

    def _domain(self, url):
        """Extract domain from URL."""
        return url.split("/")[2]

    def _wait_rate_limit(self, domain):
        """Sleep if needed to respect per-domain rate limit."""
        limit = self._rate_limits.get(domain, 1.0)  # default 1 req/s
        last = self._last_request.get(domain, 0)
        elapsed = time.time() - last
        if elapsed < limit:
            time.sleep(limit - elapsed)
        self._last_request[domain] = time.time()

    def get(self, url, max_retries=3, extra_headers=None):
        """GET with rate limiting, If-Modified-Since, and exponential backoff.

        Returns requests.Response or None on 304 Not Modified.
        Raises requests.HTTPError on non-retryable failures.
        """
        domain = self._domain(url)
        self._wait_rate_limit(domain)

        headers = {}
        if url in self._last_modified:
            headers["If-Modified-Since"] = self._last_modified[url]
        if extra_headers:
            headers.update(extra_headers)

        last_exc = None
        for attempt in range(max_retries):
            try:
                r = self.session.get(url, headers=headers, timeout=self.timeout)

                if r.status_code == 304:
                    return None

                if r.status_code == 429 or r.status_code >= 500:
                    wait = (2 ** attempt) * 1.0
                    time.sleep(wait)
                    last_exc = requests.HTTPError(
                        f"{r.status_code} for {url}", response=r
                    )
                    continue

                r.raise_for_status()

                # Track Last-Modified for future conditional requests
                lm = r.headers.get("Last-Modified")
                if lm:
                    self._last_modified[url] = lm

                return r

            except requests.ConnectionError as e:
                last_exc = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue
            except requests.Timeout as e:
                last_exc = e
                if attempt < max_retries - 1:
                    time.sleep(2 ** attempt)
                continue

        if last_exc:
            raise last_exc
        return None

    def get_json(self, url, max_retries=3, extra_headers=None):
        """GET and parse JSON. Returns parsed data or None on 304."""
        r = self.get(url, max_retries=max_retries, extra_headers=extra_headers)
        if r is None:
            return None
        return r.json()

    def get_text(self, url, encoding=None, max_retries=3, extra_headers=None):
        """GET and return decoded text with explicit encoding."""
        r = self.get(url, max_retries=max_retries, extra_headers=extra_headers)
        if r is None:
            return None
        if encoding:
            r.encoding = encoding
        return r.text

    def set_last_modified(self, url, value):
        """Seed a Last-Modified value from persistent cache."""
        if value:
            self._last_modified[url] = value

    def get_last_modified(self, url):
        """Get the Last-Modified value for a URL (if any)."""
        return self._last_modified.get(url)

