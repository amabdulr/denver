#!/usr/bin/env python3
"""
Re-download systems-interfaces chapters from the correct static URL pattern.

The inventory has JS-rendered URLs that return empty shells.
The static versions live at:
  .../sdwan/17-x/systems-interfaces/systems-interfaces-guide-17-x/{slug}.html

Usage:
  python scripts/fix_sysint_download.py --test        # test 1 chapter
  python scripts/fix_sysint_download.py               # download all 66
"""
import argparse
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert

PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
HTML_DIR = os.path.join(PROJECT_ROOT, "data", "html_archive", "sdwan", "systems-interfaces-book-xe-sdwan")
MD_DIR = os.path.join(PROJECT_ROOT, "knowledge_docs", "sdwan", "systems-interfaces-book-xe-sdwan")

TOC_URL = "https://www.cisco.com/c/en/us/td/docs/routers/sdwan/17-x/systems-interfaces/systems-interfaces-guide-17-x.html"
BASE_URL = "https://www.cisco.com/c/en/us/td/docs/routers/sdwan/17-x/systems-interfaces/systems-interfaces-guide-17-x"


def get_chapter_list():
    """Scrape the TOC sidebar for all chapter slugs and titles."""
    resp = requests.get(TOC_URL, timeout=30)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")

    chapters = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if "systems-interfaces-guide-17-x/" in href and href.endswith(".html"):
            slug = href.rsplit("/", 1)[-1].replace(".html", "")
            if slug not in seen:
                seen.add(slug)
                title = a.get_text(strip=True)
                url = f"{BASE_URL}/{slug}.html"
                chapters.append({"slug": slug, "title": title, "url": url})
    return chapters


def download_and_convert(chapter, verbose=True):
    """Download one chapter's HTML and convert to Markdown. Returns (ok, size_kb)."""
    slug = chapter["slug"]
    url = chapter["url"]
    html_path = os.path.join(HTML_DIR, f"{slug}.html")
    md_path = os.path.join(MD_DIR, f"{slug}.md")

    # Download
    resp = requests.get(url, timeout=30)
    resp.raise_for_status()
    html_bytes = resp.content
    with open(html_path, "wb") as f:
        f.write(html_bytes)

    # Convert
    soup = BeautifulSoup(html_bytes, "html.parser")
    for tag in soup(["nav", "header", "footer", "script", "style", "aside", "noscript", "iframe"]):
        tag.decompose()

    best = soup.find("div", id="chapterContent")
    if best is None:
        # fallback to largest container
        candidates = [soup.find("main"), soup.find("article"), soup.body]
        best = soup
        best_len = 0
        for c in candidates:
            if c is not None:
                tl = len(c.get_text(strip=True))
                if tl > best_len:
                    best = c
                    best_len = tl

    md_text = md_convert(str(best), heading_style="ATX", strip=["img"])
    with open(md_path, "w") as f:
        f.write(md_text)

    size_kb = len(md_text) / 1024
    content_chars = len(best.get_text(strip=True))

    if verbose:
        status = "OK" if size_kb > 2 else "WARN"
        print(f"  {status} {slug} -> {size_kb:.0f} KB md ({content_chars:,} chars content)")

    return size_kb > 2, size_kb


def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--test", action="store_true", help="Test with 1 chapter only")
    args = parser.parse_args()

    os.makedirs(HTML_DIR, exist_ok=True)
    os.makedirs(MD_DIR, exist_ok=True)

    print("Fetching chapter list from TOC...")
    chapters = get_chapter_list()
    print(f"Found {len(chapters)} chapters\n")

    if args.test:
        # Pick etherchann as the test — we know what the good output looks like
        test_ch = next((c for c in chapters if c["slug"] == "etherchann"), chapters[5])
        print(f"Test download: {test_ch['slug']} ({test_ch['title']})")
        print(f"  URL: {test_ch['url']}")
        ok, size = download_and_convert(test_ch)
        md_path = os.path.join(MD_DIR, f"{test_ch['slug']}.md")
        print(f"\nResult: {'PASS' if ok else 'FAIL'} — {size:.0f} KB")
        print(f"Preview (first 500 chars):")
        with open(md_path) as f:
            print(f.read()[:500])
        return

    # Full run — clean old broken files first
    old_files = [f for f in os.listdir(MD_DIR) if f.endswith(".md")]
    old_slugs = {f.replace(".md", "") for f in old_files}
    new_slugs = {c["slug"] for c in chapters}
    orphans = old_slugs - new_slugs
    if orphans:
        print(f"Removing {len(orphans)} orphan .md files from old inventory...")
        for slug in orphans:
            for d, ext in [(MD_DIR, ".md"), (HTML_DIR, ".html")]:
                p = os.path.join(d, slug + ext)
                if os.path.exists(p):
                    os.remove(p)
                    print(f"  removed {slug}{ext}")

    downloaded = 0
    failed = 0
    for ch in chapters:
        try:
            ok, _ = download_and_convert(ch)
            downloaded += 1
            if not ok:
                print(f"  ^ WARNING: small output")
        except Exception as e:
            print(f"  FAIL {ch['slug']}: {e}")
            failed += 1
        time.sleep(0.3)

    print(f"\nDone: {downloaded} downloaded, {failed} failed")
    print(f"Markdown: {MD_DIR}")
    print(f"HTML archive: {HTML_DIR}")


if __name__ == "__main__":
    main()
