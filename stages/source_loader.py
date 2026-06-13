#!/usr/bin/env python3
"""Resolve sources from project config file + CLI arguments."""

import os
import re


def parse_sources_file(filepath):
    """Parse a sources.md file and return list of URLs/file paths."""
    if not os.path.exists(filepath):
        return []

    sources = []
    with open(filepath, "r") as f:
        for line in f:
            # Match markdown links: [text](url)
            md_match = re.search(r'\[.*?\]\((https?://[^\s)]+)\)', line)
            if md_match:
                url = md_match.group(1).rstrip("/")
                if url not in sources:
                    sources.append(url)
                continue

            # Match bare URLs
            url_match = re.search(r'(https?://[^\s|]+)', line)
            if url_match:
                url = url_match.group(0).rstrip("/").strip()
                url = re.sub(r'[|>]+$', '', url).strip()
                if url and url not in sources:
                    sources.append(url)
                continue

            # Match local file paths (lines that look like paths)
            stripped = line.strip()
            if stripped and (
                stripped.startswith("./")
                or stripped.startswith("/")
                or stripped.startswith("~/")
                or (
                    os.path.exists(stripped)
                    and not stripped.startswith("#")
                )
            ):
                path = os.path.expanduser(stripped)
                if os.path.exists(path) and path not in sources:
                    sources.append(path)

    return sources


def load_sources(project_dir, extra_sources=None):
    """Load sources from project's sources.md, merge with extra_sources, deduplicate.

    Returns list of dicts: [{url: str, type: 'url'|'file'}, ...]
    """
    sources_file = os.path.join(project_dir, "sources.md")
    raw = parse_sources_file(sources_file)

    if extra_sources:
        for s in extra_sources:
            if s not in raw:
                raw.append(s)

    result = []
    seen = set()
    for s in raw:
        if s in seen:
            continue
        seen.add(s)
        if s.startswith("http://") or s.startswith("https://"):
            result.append({"url": s, "type": "url"})
        else:
            result.append({"url": s, "type": "file"})

    return result
