"""
Admin download script — Cisco SD-WAN chapter HTML pages.

Two-step pipeline:
  1. Download raw HTML from cisco.com → data/html_archive/sdwan/<book>/<chapter>.html
  2. Convert HTML → Markdown         → knowledge_docs/sdwan/<book>/<chapter>.md

The HTML archive is the source of truth; the Markdown files are what
the ingestion pipeline reads into ChromaDB.

Can be used standalone or called from the Admin UI.
"""

import json
import os
import re
import sys
import time

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INVENTORY_PATH = os.path.join(
    PROJECT_ROOT, "inventory", "sdwan", "document_inventory.json"
)
HTML_ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "data", "html_archive", "sdwan")
MARKDOWN_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "knowledge_docs", "sdwan")

REQUEST_TIMEOUT = 30
DELAY_BETWEEN = 0.3
MIN_CONTENT_CHARS = 2000  # below this → likely JS-rendered shell
HTTP_RETRIES = 2

# Some books have JS-rendered pages at the inventory URLs but a static
# version at a different URL path.  Map book-slug → static TOC URL.
# The TOC sidebar will be scraped for real chapter links.
STATIC_BOOK_OVERRIDES = {
    "systems-interfaces-book-xe-sdwan": (
        "https://www.cisco.com/c/en/us/td/docs/routers/sdwan/17-x/"
        "systems-interfaces/systems-interfaces-guide-17-x.html"
    ),
}

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}


def _book_slug(key: str) -> str:
    return key.replace(".pdf", "")


def _fetch(url: str):
    """Return (html_bytes, error_string|None)."""
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
            if resp.status_code == 200:
                return resp.content, None
            return None, f"HTTP {resp.status_code}"
        except requests.exceptions.Timeout:
            if attempt >= HTTP_RETRIES:
                return None, "timeout"
        except requests.exceptions.ConnectionError:
            if attempt >= HTTP_RETRIES:
                return None, "connection_error"
        time.sleep(3 * attempt)
    return None, "max_retries"


def _scrape_static_toc(toc_url: str) -> list:
    """Scrape a static book TOC page for chapter slug/title/URL triples."""
    resp = requests.get(toc_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    # Derive base URL from the TOC URL (strip trailing .html filename)
    base = toc_url.rsplit("/", 1)[0]
    chapters = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        # Only links pointing into this same book directory
        book_dir = toc_url.rsplit("/", 1)[-1].replace(".html", "")
        if f"{book_dir}/" in href and href.endswith(".html"):
            slug = href.rsplit("/", 1)[-1].replace(".html", "")
            if slug not in seen:
                seen.add(slug)
                title = a.get_text(strip=True)
                chapters.append({
                    "chapter_slug": slug,
                    "chapter_title": title,
                    "chapter_url": f"{base}/{slug}.html",
                })
    return chapters


def _is_js_rendered(html_bytes: bytes) -> bool:
    soup = BeautifulSoup(html_bytes, "html.parser")
    for tag in soup(["script", "style", "noscript"]):
        tag.decompose()
    return len(soup.get_text(strip=True)) < MIN_CONTENT_CHARS


def _html_to_markdown(html_bytes: bytes) -> str:
    """Convert raw HTML bytes to clean Markdown, extracting chapter content."""
    soup = BeautifulSoup(html_bytes, "html.parser")

    for tag in soup(["nav", "header", "footer", "script", "style",
                     "aside", "noscript", "iframe"]):
        tag.decompose()

    # Cisco.com puts chapter text in div#chapterContent
    best = soup.find("div", id="chapterContent")
    if best is None:
        candidates = [
            soup.find("main"),
            soup.find("div", class_=re.compile(r"\bwide-v2\b")),
            soup.find("article"),
            soup.find("div", class_=re.compile(r"\b(content|body|main)\b", re.I)),
            soup.body,
        ]
        best = soup
        best_len = 0
        for c in candidates:
            if c is not None:
                tl = len(c.get_text(strip=True))
                if tl > best_len:
                    best = c
                    best_len = tl

    return md_convert(str(best), heading_style="ATX", strip=["img"])


def run_download(download_dir=None, target_release=None, log=print, book_filter=None, force=False):
    """
    Download HTML for every chapter, then convert to Markdown.

    Args:
        download_dir:   Ignored (kept for Admin API compat). HTML goes to
                        data/html_archive/sdwan/, Markdown to knowledge_docs/sdwan/.
        target_release: Ignored for HTML chapter downloads.
        log:            Callable(str) for progress messages.
        book_filter:    Optional book slug to download only one book.
        force:          Re-download and reconvert even if files already exist.

    Returns:
        list[tuple]: [(name, success_bool, message), ...]
    """
    os.makedirs(HTML_ARCHIVE_DIR, exist_ok=True)
    os.makedirs(MARKDOWN_OUTPUT_DIR, exist_ok=True)

    with open(INVENTORY_PATH) as fh:
        inventory = json.load(fh)

    results = []
    total = sum(len(b.get("chapters", [])) for b in inventory.values())
    log(f"Inventory: {len(inventory)} books, {total} chapters")
    log(f"HTML archive:  {HTML_ARCHIVE_DIR}")
    log(f"Markdown output: {MARKDOWN_OUTPUT_DIR}")

    downloaded = 0
    converted = 0
    skipped = 0
    failed = 0

    for book_key, book_data in inventory.items():
        slug = _book_slug(book_key)
        if book_filter and slug != book_filter:
            continue

        # Use static TOC override if available (some books have JS-rendered
        # inventory URLs but a working static version at a different path).
        if slug in STATIC_BOOK_OVERRIDES:
            toc_url = STATIC_BOOK_OVERRIDES[slug]
            log(f"\n📚 {slug} (static override)")
            try:
                chapters = _scrape_static_toc(toc_url)
                log(f"   Scraped {len(chapters)} chapters from static TOC")
            except Exception as exc:
                log(f"   ❌ Failed to scrape static TOC: {exc}")
                chapters = book_data.get("chapters", [])
                log(f"   Falling back to inventory ({len(chapters)} chapters)")
        else:
            chapters = book_data.get("chapters", [])

        html_book_dir = os.path.join(HTML_ARCHIVE_DIR, slug)
        md_book_dir = os.path.join(MARKDOWN_OUTPUT_DIR, slug)
        os.makedirs(html_book_dir, exist_ok=True)
        os.makedirs(md_book_dir, exist_ok=True)
        log(f"   📂 {len(chapters)} chapters")

        for ch in chapters:
            ch_slug = ch["chapter_slug"]
            ch_url = ch["chapter_url"]
            html_path = os.path.join(html_book_dir, f"{ch_slug}.html")
            md_path = os.path.join(md_book_dir, f"{ch_slug}.md")

            # If markdown already exists and HTML is cached, skip (unless forced)
            if not force and os.path.exists(md_path) and os.path.exists(html_path):
                results.append((f"{slug}/{ch_slug}", True, "already exists"))
                skipped += 1
                continue

            # Step 1: Download HTML (skip if already cached, unless forced)
            if not force and os.path.exists(html_path):
                with open(html_path, "rb") as f:
                    html_bytes = f.read()
            else:
                html_bytes, err = _fetch(ch_url)
                if html_bytes is None:
                    log(f"  ❌ {ch_slug} — {err}")
                    results.append((f"{slug}/{ch_slug}", False, err))
                    failed += 1
                    continue

                js_warn = ""
                if _is_js_rendered(html_bytes):
                    js_warn = " ⚠ JS-rendered?"

                with open(html_path, "wb") as f:
                    f.write(html_bytes)
                downloaded += 1
                time.sleep(DELAY_BETWEEN)

            # Step 2: Convert HTML → Markdown
            try:
                markdown = _html_to_markdown(html_bytes)
                with open(md_path, "w", encoding="utf-8") as f:
                    f.write(markdown)
                converted += 1
                size_kb = len(markdown) / 1024
                js_warn = js_warn if 'js_warn' in dir() else ""
                log(f"  ✅ {ch_slug} → {size_kb:.0f} KB md{js_warn}")
                results.append((f"{slug}/{ch_slug}", True, "ok"))
            except Exception as exc:
                log(f"  ⚠️  {ch_slug} — convert error: {exc}")
                results.append((f"{slug}/{ch_slug}", False, str(exc)))
                failed += 1

    ok = sum(1 for r in results if r[1])
    log(f"\n{'='*50}")
    log(f"Downloaded: {downloaded}  Converted: {converted}  Skipped: {skipped}  Failed: {failed}")
    log(f"Markdown files in: {MARKDOWN_OUTPUT_DIR}")
    return results


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(description="Download SD-WAN chapter HTML → Markdown")
    parser.add_argument("--book", help="Download only this book slug")
    parser.add_argument("--dry-run", action="store_true")
    parser.add_argument("--reconvert", action="store_true",
                        help="Re-convert existing HTML to Markdown (no download)")
    parser.add_argument("--force", action="store_true",
                        help="Re-download and reconvert even if files already exist")
    args = parser.parse_args()

    if args.dry_run:
        with open(INVENTORY_PATH) as fh:
            inv = json.load(fh)
        for bk, bd in inv.items():
            s = _book_slug(bk)
            if args.book and s != args.book:
                continue
            if s in STATIC_BOOK_OVERRIDES:
                chs = _scrape_static_toc(STATIC_BOOK_OVERRIDES[s])
                print(f"{s}: {len(chs)} chapters (static override)")
            else:
                chs = bd.get("chapters", [])
                print(f"{s}: {len(chs)} chapters")
            for c in chs:
                print(f"  {c['chapter_slug']}")
    elif args.reconvert:
        # Re-convert all cached HTML without re-downloading
        with open(INVENTORY_PATH) as fh:
            inv = json.load(fh)
        count = 0
        for bk, bd in inv.items():
            s = _book_slug(bk)
            if args.book and s != args.book:
                continue
            for ch in bd.get("chapters", []):
                html_p = os.path.join(HTML_ARCHIVE_DIR, s, f"{ch['chapter_slug']}.html")
                md_p = os.path.join(MARKDOWN_OUTPUT_DIR, s, f"{ch['chapter_slug']}.md")
                if os.path.exists(html_p):
                    with open(html_p, "rb") as f:
                        markdown = _html_to_markdown(f.read())
                    os.makedirs(os.path.dirname(md_p), exist_ok=True)
                    with open(md_p, "w", encoding="utf-8") as f:
                        f.write(markdown)
                    count += 1
        print(f"Re-converted {count} chapters")
    else:
        run_download(book_filter=args.book, force=args.force)
