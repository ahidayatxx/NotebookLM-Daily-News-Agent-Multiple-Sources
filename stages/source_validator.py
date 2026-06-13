#!/usr/bin/env python3
"""Validate sources and clean sources.md of URLs that fail in NotebookLM."""

import re


def _normalize(url):
    """Normalize a URL for matching: strip trailing slash and whitespace."""
    return url.rstrip("/").strip().rstrip("|>")


def clean_sources_file(sources_md_path, urls_to_remove):
    """Rewrite sources.md, removing lines that reference any failed URL.

    Returns the number of lines removed.
    """
    if not urls_to_remove:
        return 0

    try:
        with open(sources_md_path, "r") as f:
            lines = f.readlines()
    except FileNotFoundError:
        return 0

    failed_set = {_normalize(u) for u in urls_to_remove}

    cleaned = []
    removed = 0
    for line in lines:
        line_urls = re.findall(r"https?://[^\s|)]+", line)
        line_urls_normalized = {_normalize(u) for u in line_urls}
        if line_urls_normalized & failed_set:
            removed += 1
            continue
        cleaned.append(line)

    if removed > 0:
        with open(sources_md_path, "w") as f:
            f.writelines(cleaned)

    return removed
