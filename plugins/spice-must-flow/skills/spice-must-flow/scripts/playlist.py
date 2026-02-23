#!/usr/bin/env python3
"""Fetch a random flow playlist from the community list."""
import random
import urllib.request

URL = "https://raw.githubusercontent.com/akegaviar/spice-must-flow/main/playlists.txt"

try:
    with urllib.request.urlopen(URL, timeout=2) as r:
        lines = r.read().decode().splitlines()
        playlists = [l.strip() for l in lines if l.strip() and not l.startswith('#')]
        if playlists:
            print(random.choice(playlists))
except:
    pass  # Silent fail - music is non-critical
