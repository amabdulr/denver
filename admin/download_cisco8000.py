"""
Admin download script — Cisco 8000 Series chapter HTML pages.

Three-phase pipeline:
  Phase 1: Discover books from the cisco.com support landing page
           → build inventory/Cisco8000/document_inventory.json
  Phase 2: Download raw HTML chapters
           → data/html_archive/Cisco8000/<book>/<chapter>.html
  Phase 3: Convert HTML → Markdown
           → knowledge_docs/Cisco8000/<book>/<chapter>.md

Also provides:
  --archive   Move existing PDFs from knowledge_docs/ → pdf_archive/
  --validate  Compare inventory chapters vs Markdown files on disk
  --compare   Compare archived PDFs vs downloaded Markdown (book coverage)

Can be used standalone or called from the Admin UI.
"""

import glob
import json
import os
import re
import shutil
import time

import requests
from bs4 import BeautifulSoup
from markdownify import markdownify as md_convert
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

# ---------------------------------------------------------------------------
# Paths
# ---------------------------------------------------------------------------
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)

INVENTORY_DIR = os.path.join(PROJECT_ROOT, "inventory", "Cisco8000")
INVENTORY_PATH = os.path.join(INVENTORY_DIR, "document_inventory.json")
HTML_ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "data", "html_archive", "Cisco8000")
MARKDOWN_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "knowledge_docs", "Cisco8000")
PDF_ARCHIVE_DIR = os.path.join(PROJECT_ROOT, "pdf_archive", "Cisco8000")

# ---------------------------------------------------------------------------
# Constants
# ---------------------------------------------------------------------------
BASE_URL = "https://www.cisco.com"
LANDING_PAGES = [
    # Configuration guides
    "https://www.cisco.com/c/en/us/support/routers/"
    "8000-series-routers/products-installation-and-configuration-guides-list.html",
    # Install & upgrade guides (hardware install guides live here)
    "https://www.cisco.com/c/en/us/support/routers/"
    "8000-series-routers/products-installation-guides-list.html",
]

REQUEST_TIMEOUT = 30
DELAY_BETWEEN = 0.3          # seconds between HTTP requests
MIN_CONTENT_CHARS = 2000     # below this → likely JS-rendered shell
HTTP_RETRIES = 2
MAX_WORKERS = 5

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    ),
    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
}

# Links that should always be skipped from the landing page
_SKIP_PATTERNS = [
    "release/notes",
    "release-notes",
    "/mcl",
    "/videos/",
    ".zip",
    ".pdf",
    "rcsi",
]

# Books whose landing pages are JS-rendered; map slug → working static URL
STATIC_BOOK_OVERRIDES: dict[str, str] = {
    # Add entries here if any Cisco 8000 book pages return empty JS shells.
    # Example:
    # "b-segment-routing-cg-cisco8000": "https://www.cisco.com/.../static-toc.html",
}

# Extra book URLs not linked from the landing pages (e.g. cross-product guides)
EXTRA_BOOK_URLS = [
    ("https://www.cisco.com/c/en/us/td/docs/iosxr/licensing/article/"
     "ios-xr-smart-licensing-using-policy.html",
     "IOS XR Smart Licensing Using Policy"),
]

# Regex that matches release-suffixed URL slugs (e.g. "-26xx", "-711x", "-79x")
_RELEASE_SUFFIX_RE = re.compile(r"-\d{2,3}x{1,2}(\.html)?$", re.IGNORECASE)


# ═══════════════════════════════════════════════════════════════════════════
# Phase 1 — Discover books + build inventory
# ═══════════════════════════════════════════════════════════════════════════

def _should_skip(href: str) -> bool:
    href_lower = href.lower()
    return any(pat in href_lower for pat in _SKIP_PATTERNS)


def _discover_books(target_release=None, log=print):
    """Scrape all landing pages and return a list of (book_url, link_text)."""
    books = {}  # url → link_text

    for page_url in LANDING_PAGES:
        label = "install" if "installation-guides-list" in page_url else "config"
        log(f"Fetching {label} landing page…")
        resp = requests.get(page_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        resp.raise_for_status()
        soup = BeautifulSoup(resp.text, "html.parser")

        for a in soup.find_all("a", href=True):
            href = a["href"]
            if "/td/docs/" not in href:
                continue
            if _should_skip(href):
                continue
            full_url = urljoin(BASE_URL, href)
            if target_release:
                slug_tail = full_url.rstrip("/").split("/")[-1]
                has_release_suffix = bool(_RELEASE_SUFFIX_RE.search(slug_tail))
                if has_release_suffix:
                    # Release-versioned book → keep only if it matches
                    rel_major = target_release.split(".")[0]
                    text = a.get_text(strip=True)
                    if (rel_major not in href
                            and target_release not in href
                            and target_release not in text):
                        continue
                # else: no release suffix → always keep (HIG, migration, etc.)
            if full_url not in books:
                books[full_url] = a.get_text(strip=True)

    # Append extra (manually curated) book URLs
    for url, label in EXTRA_BOOK_URLS:
        if url not in books:
            books[url] = label

    log(f"Found {len(books)} book landing pages")
    return list(books.items())


def _url_to_book_slug(url: str) -> str:
    """Derive a book slug from a cisco.com book URL."""
    return url.rstrip("/").split("/")[-1].replace(".html", "")


def _scrape_title(url: str) -> str:
    """Fetch a page and return its <title> text."""
    try:
        resp = requests.get(url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")
        tag = soup.find("title")
        if tag:
            return tag.get_text(strip=True).split(" - Cisco")[0].strip()
    except Exception:
        pass
    return ""


def _scrape_chapters(source_url: str) -> list[dict]:
    """Scrape a book's landing page for chapter links."""
    try:
        resp = requests.get(source_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
        soup = BeautifulSoup(resp.text, "html.parser")
        book_slug = _url_to_book_slug(source_url)

        chapters = []
        seen = set()
        for a in soup.find_all("a", href=True):
            href = a["href"]
            text = a.get_text(strip=True)
            if (book_slug in href
                    and text and len(text) > 3
                    and not href.endswith(".pdf")):
                full_url = urljoin(BASE_URL, href)
                if full_url in seen:
                    continue
                seen.add(full_url)
                ch_slug = full_url.rstrip("/").split("/")[-1].replace(".html", "")
                if ch_slug == book_slug or "login" in href:
                    continue
                chapters.append({
                    "chapter_slug": ch_slug,
                    "chapter_title": text,
                    "chapter_url": full_url,
                })
        return chapters
    except Exception:
        return []


def _scrape_static_toc(toc_url: str) -> list[dict]:
    """Scrape a static TOC page for chapter links (for JS-rendered books)."""
    resp = requests.get(toc_url, headers=HEADERS, timeout=REQUEST_TIMEOUT)
    resp.raise_for_status()
    soup = BeautifulSoup(resp.content, "html.parser")
    base = toc_url.rsplit("/", 1)[0]
    book_dir = toc_url.rsplit("/", 1)[-1].replace(".html", "")
    chapters = []
    seen = set()
    for a in soup.find_all("a", href=True):
        href = a["href"]
        if f"{book_dir}/" in href and href.endswith(".html"):
            slug = href.rsplit("/", 1)[-1].replace(".html", "")
            if slug not in seen:
                seen.add(slug)
                chapters.append({
                    "chapter_slug": slug,
                    "chapter_title": a.get_text(strip=True),
                    "chapter_url": f"{base}/{slug}.html",
                })
    return chapters


def build_inventory(target_release=None, log=print):
    """Discover books, scrape chapters, write document_inventory.json."""
    os.makedirs(INVENTORY_DIR, exist_ok=True)

    # Load existing to preserve manual edits
    inventory = {}
    if os.path.exists(INVENTORY_PATH):
        with open(INVENTORY_PATH) as f:
            inventory = json.load(f)

    book_urls = _discover_books(target_release=target_release, log=log)

    new_books = 0
    for url, link_text in book_urls:
        slug = _url_to_book_slug(url)
        book_key = f"{slug}.pdf"  # key format matches SD-WAN convention
        if book_key in inventory and inventory[book_key].get("chapters"):
            continue
        title = _scrape_title(url) or link_text or slug.replace("-", " ").title()
        log(f"  📚 {slug}")

        if slug in STATIC_BOOK_OVERRIDES:
            chapters = _scrape_static_toc(STATIC_BOOK_OVERRIDES[slug])
            log(f"     {len(chapters)} chapters (static override)")
        else:
            chapters = _scrape_chapters(url)
            log(f"     {len(chapters)} chapters")

        inventory[book_key] = {
            "title": title,
            "source_url": url,
            "chapters": chapters,
        }
        new_books += 1
        time.sleep(DELAY_BETWEEN)

    total_ch = sum(len(v.get("chapters", [])) for v in inventory.values())
    log(f"\n📋 Inventory: {len(inventory)} books, {total_ch} chapters "
        f"({new_books} new)")

    with open(INVENTORY_PATH, "w") as f:
        json.dump(inventory, f, indent=2)
    log(f"   Saved to {INVENTORY_PATH}")
    return inventory


# ═══════════════════════════════════════════════════════════════════════════
# Phase 2+3 — Download HTML chapters → convert to Markdown
# ═══════════════════════════════════════════════════════════════════════════

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


def _book_slug(key: str) -> str:
    return key.replace(".pdf", "")


def _download_and_convert(inventory, book_filter=None, force=False, log=print):
    """Download HTML for every chapter and convert to Markdown."""
    os.makedirs(HTML_ARCHIVE_DIR, exist_ok=True)
    os.makedirs(MARKDOWN_OUTPUT_DIR, exist_ok=True)

    results = []
    total = sum(len(b.get("chapters", [])) for b in inventory.values())
    log(f"\nInventory: {len(inventory)} books, {total} chapters")
    log(f"HTML archive:    {HTML_ARCHIVE_DIR}")
    log(f"Markdown output: {MARKDOWN_OUTPUT_DIR}")

    downloaded = 0
    converted = 0
    skipped = 0
    failed = 0

    for book_key, book_data in inventory.items():
        slug = _book_slug(book_key)
        if book_filter and slug != book_filter:
            continue

        if slug in STATIC_BOOK_OVERRIDES:
            log(f"\n📚 {slug} (static override)")
            try:
                chapters = _scrape_static_toc(STATIC_BOOK_OVERRIDES[slug])
                log(f"   Scraped {len(chapters)} chapters from static TOC")
            except Exception as exc:
                log(f"   ❌ Failed to scrape static TOC: {exc}")
                chapters = book_data.get("chapters", [])
                log(f"   Falling back to inventory ({len(chapters)} chapters)")
        else:
            chapters = book_data.get("chapters", [])
            log(f"\n📚 {slug} — {len(chapters)} chapters")

        html_book_dir = os.path.join(HTML_ARCHIVE_DIR, slug)
        md_book_dir = os.path.join(MARKDOWN_OUTPUT_DIR, slug)
        os.makedirs(html_book_dir, exist_ok=True)
        os.makedirs(md_book_dir, exist_ok=True)

        for ch in chapters:
            ch_slug = ch["chapter_slug"]
            ch_url = ch["chapter_url"]
            html_path = os.path.join(html_book_dir, f"{ch_slug}.html")
            md_path = os.path.join(md_book_dir, f"{ch_slug}.md")

            if not force and os.path.exists(md_path) and os.path.exists(html_path):
                results.append((f"{slug}/{ch_slug}", True, "already exists"))
                skipped += 1
                continue

            # Step 1: Download HTML (use cache if available)
            js_warn = ""
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
                log(f"  ✅ {ch_slug} → {size_kb:.0f} KB md{js_warn}")
                results.append((f"{slug}/{ch_slug}", True, "ok"))
            except Exception as exc:
                log(f"  ⚠️  {ch_slug} — convert error: {exc}")
                results.append((f"{slug}/{ch_slug}", False, str(exc)))
                failed += 1

    log(f"\n{'='*50}")
    log(f"Downloaded: {downloaded}  Converted: {converted}  "
        f"Skipped: {skipped}  Failed: {failed}")
    log(f"Markdown files in: {MARKDOWN_OUTPUT_DIR}")
    return results


# ═══════════════════════════════════════════════════════════════════════════
# Post-download utilities
# ═══════════════════════════════════════════════════════════════════════════

def archive_pdfs(log=print):
    """Move PDFs from knowledge_docs/Cisco8000/ → pdf_archive/Cisco8000/."""
    os.makedirs(PDF_ARCHIVE_DIR, exist_ok=True)
    pdfs = sorted(glob.glob(os.path.join(MARKDOWN_OUTPUT_DIR, "*.pdf")))
    if not pdfs:
        log("📦 No PDFs to archive.")
        return 0

    moved = 0
    for pdf in pdfs:
        fname = os.path.basename(pdf)
        dest = os.path.join(PDF_ARCHIVE_DIR, fname)
        if os.path.exists(dest):
            log(f"   ⏭️  {fname} (already in archive)")
        else:
            shutil.move(pdf, dest)
            log(f"   📦 {fname} → pdf_archive/Cisco8000/")
            moved += 1

    log(f"Archived {moved} PDF(s) to {PDF_ARCHIVE_DIR}")
    return moved


def validate_coverage(log=print):
    """Compare inventory chapters vs actual Markdown files on disk."""
    if not os.path.exists(INVENTORY_PATH):
        log("⚠️  No inventory file — run download first.")
        return {}

    with open(INVENTORY_PATH) as f:
        inventory = json.load(f)

    missing = []
    found = 0
    total_ch = 0

    for book_key, book_data in inventory.items():
        slug = _book_slug(book_key)
        chapters = book_data.get("chapters", [])
        total_ch += len(chapters)
        for ch in chapters:
            md_path = os.path.join(MARKDOWN_OUTPUT_DIR, slug,
                                   f"{ch['chapter_slug']}.md")
            if os.path.exists(md_path):
                found += 1
            else:
                missing.append(f"{slug}/{ch['chapter_slug']}.md")

    log(f"\n📊 Coverage Report — Cisco 8000")
    log(f"   Books in inventory:    {len(inventory)}")
    log(f"   Chapters in inventory: {total_ch}")
    log(f"   Markdown files found:  {found}/{total_ch}")
    if missing:
        log(f"   ❌ Missing ({len(missing)}):")
        for m in missing[:20]:
            log(f"      {m}")
        if len(missing) > 20:
            log(f"      … and {len(missing) - 20} more")
    else:
        log("   ✅ All chapters have Markdown files")

    return {"total_books": len(inventory), "total_chapters": total_ch,
            "found": found, "missing": missing}


def compare_pdfs_vs_markdown(log=print):
    """Compare archived PDFs against downloaded Markdown book folders.

    For each archived PDF, checks whether a corresponding book folder with
    Markdown chapters exists in knowledge_docs/Cisco8000/.  Reports:
      - PDFs with matching Markdown book folders (and chapter counts)
      - PDFs with NO Markdown equivalent (gaps to fill)
      - Markdown book folders with no corresponding archived PDF (new-only)
    """
    pdf_dir = PDF_ARCHIVE_DIR
    md_dir = MARKDOWN_OUTPUT_DIR

    # Collect archived PDFs
    if os.path.isdir(pdf_dir):
        pdfs = {os.path.splitext(f)[0]: f
                for f in os.listdir(pdf_dir) if f.endswith(".pdf")}
    else:
        pdfs = {}

    # Collect Markdown book folders
    if os.path.isdir(md_dir):
        md_books = {}
        for d in os.listdir(md_dir):
            dp = os.path.join(md_dir, d)
            if os.path.isdir(dp):
                mds = [f for f in os.listdir(dp) if f.endswith(".md")]
                md_books[d] = len(mds)
    else:
        md_books = {}

    pdf_slugs = set(pdfs.keys())
    md_slugs = set(md_books.keys())

    matched = pdf_slugs & md_slugs
    pdf_only = pdf_slugs - md_slugs
    md_only = md_slugs - pdf_slugs

    log(f"\n📊 PDF vs Markdown Comparison — Cisco 8000")
    log(f"   Archived PDFs:       {len(pdfs)}")
    log(f"   Markdown book dirs:  {len(md_books)}")

    if matched:
        log(f"\n   ✅ Matched ({len(matched)}):")
        for slug in sorted(matched):
            log(f"      {slug}: {md_books[slug]} chapters (md)  ←  {pdfs[slug]}")

    if pdf_only:
        log(f"\n   ❌ PDFs with NO Markdown ({len(pdf_only)}):")
        for slug in sorted(pdf_only):
            log(f"      {pdfs[slug]}  →  needs HTML download")

    if md_only:
        log(f"\n   ℹ️  Markdown-only (no archived PDF) ({len(md_only)}):")
        for slug in sorted(md_only):
            log(f"      {slug}/  ({md_books[slug]} chapters)")

    return {"matched": sorted(matched), "pdf_only": sorted(pdf_only),
            "md_only": sorted(md_only), "md_chapter_counts": md_books}


# ═══════════════════════════════════════════════════════════════════════════
# run_download — Admin UI entry point
# ═══════════════════════════════════════════════════════════════════════════

def run_download(download_dir=None, target_release=None, log=print,
                 book_filter=None, force=False):
    """
    Full pipeline: discover books → build inventory → download HTML → convert.

    Args:
        download_dir:   Ignored (kept for Admin API compat).
        target_release: Optional release filter for book discovery.
        log:            Callable(str) for progress messages.
        book_filter:    Optional book slug to download only one book.
        force:          Re-download and reconvert even if files already exist.

    Returns:
        list[tuple]: [(name, success_bool, message), ...]
    """
    # Phase 1: Build / refresh inventory
    inventory = build_inventory(target_release=target_release, log=log)

    # Phase 2+3: Download HTML chapters → convert to Markdown
    results = _download_and_convert(
        inventory, book_filter=book_filter, force=force, log=log
    )
    return results


def download_from_inventory(log=print, book_filter=None, force=False):
    """Download + convert using the saved inventory (no re-scraping)."""
    with open(INVENTORY_PATH, encoding="utf-8") as fh:
        inventory = json.load(fh)
    log(f"Loaded inventory: {len(inventory)} books")
    return _download_and_convert(
        inventory, book_filter=book_filter, force=force, log=log
    )


# ═══════════════════════════════════════════════════════════════════════════
# CLI
# ═══════════════════════════════════════════════════════════════════════════

if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser(
        description="Cisco 8000: discover books → download HTML → convert to Markdown"
    )
    parser.add_argument("--book", help="Download only this book slug")
    parser.add_argument("--release", help="Target release (e.g. 25.1)")
    parser.add_argument("--force", action="store_true",
                        help="Re-download and reconvert even if files exist")
    parser.add_argument("--dry-run", action="store_true",
                        help="Build inventory only, list books+chapters, no download")
    parser.add_argument("--reconvert", action="store_true",
                        help="Re-convert cached HTML to Markdown (no network)")
    parser.add_argument("--archive", action="store_true",
                        help="Move PDFs from knowledge_docs/ → pdf_archive/")
    parser.add_argument("--validate", action="store_true",
                        help="Check inventory chapters vs Markdown on disk")
    parser.add_argument("--compare", action="store_true",
                        help="Compare archived PDFs vs Markdown book folders")
    args = parser.parse_args()

    if args.validate:
        validate_coverage()
    elif args.compare:
        compare_pdfs_vs_markdown()
    elif args.archive:
        archive_pdfs()
    elif args.dry_run:
        inv = build_inventory(target_release=args.release)
        print()
        for bk, bd in inv.items():
            s = _book_slug(bk)
            if args.book and s != args.book:
                continue
            chs = bd.get("chapters", [])
            print(f"{s}: {len(chs)} chapters")
            for c in chs:
                print(f"  {c['chapter_slug']}")
    elif args.reconvert:
        if not os.path.exists(INVENTORY_PATH):
            print("No inventory — run without --reconvert first.")
            raise SystemExit(1)
        with open(INVENTORY_PATH) as fh:
            inv = json.load(fh)
        count = 0
        for bk, bd in inv.items():
            s = _book_slug(bk)
            if args.book and s != args.book:
                continue
            for ch in bd.get("chapters", []):
                html_p = os.path.join(HTML_ARCHIVE_DIR, s,
                                      f"{ch['chapter_slug']}.html")
                md_p = os.path.join(MARKDOWN_OUTPUT_DIR, s,
                                    f"{ch['chapter_slug']}.md")
                if os.path.exists(html_p):
                    with open(html_p, "rb") as f:
                        markdown = _html_to_markdown(f.read())
                    os.makedirs(os.path.dirname(md_p), exist_ok=True)
                    with open(md_p, "w", encoding="utf-8") as f:
                        f.write(markdown)
                    count += 1
        print(f"Re-converted {count} chapters")
    else:
        run_download(book_filter=args.book, target_release=args.release,
                     force=args.force)
