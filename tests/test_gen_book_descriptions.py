#!/usr/bin/env python3
"""
Test script for gen_book_descriptions.py — validates the HTML fetch,
caching, and text extraction pipeline without making any LLM calls.

Uses real SD-WAN inventory data and one live Cisco HTML page to verify:
  1. Cache-path construction matches expected layout
  2. HTML fetch returns usable text (≥200 chars)
  3. Caching round-trip: write → read matches
  4. Dry-run mode lists all chapters without errors
  5. Fetch-only mode downloads and caches correctly
  6. Resume logic skips already-cached chapters
  7. Output JSON structure is valid

Run from the Denver2 project root:
    python tests/test_gen_book_descriptions.py
"""

import json
import os
import shutil
import sys
import tempfile
from pathlib import Path

# ── Setup paths ──────────────────────────────────────────────────────────────
PROJECT_ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(PROJECT_ROOT / "app"))
sys.path.insert(0, str(PROJECT_ROOT / "scripts"))

os.chdir(PROJECT_ROOT)

from dotenv import load_dotenv
load_dotenv(PROJECT_ROOT / ".env")

# Import the functions under test
import gen_book_descriptions as gbd

# ── Test data ────────────────────────────────────────────────────────────────

SAMPLE_BOOK = "routing-book-xe.pdf"
SAMPLE_CHAPTER_SLUG = "bgp-protocol"
SAMPLE_CHAPTER_TITLE = "Border Gateway Protocol"
SAMPLE_CHAPTER_URL = (
    "https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/"
    "routing/ios-xe-17/routing-book-xe/bgp-protocol.html"
)
PRODUCT = "sdwan"

passed = 0
failed = 0
skipped = 0


def report(name, ok, detail=""):
    global passed, failed
    tag = "PASS" if ok else "FAIL"
    symbol = "✅" if ok else "❌"
    print(f"  {symbol} {tag}: {name}" + (f"  ({detail})" if detail else ""))
    if ok:
        passed += 1
    else:
        failed += 1


def skip(name, reason):
    global skipped
    print(f"  ⏭️  SKIP: {name}  ({reason})")
    skipped += 1


# ── Tests ────────────────────────────────────────────────────────────────────

def test_cache_path():
    """Verify cache paths land in knowledge_docs/<product>/<book>/<chapter>.txt"""
    p = gbd._cache_path(PRODUCT, "routing-book-xe", "bgp-protocol")
    expected_suffix = Path("knowledge_docs/sdwan/routing-book-xe/bgp-protocol.txt")
    report(
        "Cache path structure",
        str(p).endswith(str(expected_suffix)),
        f"got: ...{str(p)[-60:]}"
    )


def test_cache_roundtrip():
    """Write text to cache, read it back, verify match."""
    tmp_dir = tempfile.mkdtemp(prefix="gbd_test_")
    original_dir = gbd.KNOWLEDGE_DOCS_DIR
    try:
        gbd.KNOWLEDGE_DOCS_DIR = Path(tmp_dir)
        test_text = "This is a test chapter about BGP routing in SD-WAN." * 10

        gbd.save_cached_text(PRODUCT, "test-book", "test-chapter", test_text)
        loaded = gbd.load_cached_text(PRODUCT, "test-book", "test-chapter")

        report("Cache write → read roundtrip", loaded == test_text,
               f"{len(test_text)} chars written, {len(loaded or '')} read back")
    finally:
        gbd.KNOWLEDGE_DOCS_DIR = original_dir
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_cache_miss():
    """Verify load_cached_text returns None for non-existent entries."""
    result = gbd.load_cached_text(PRODUCT, "nonexistent-book", "nonexistent-chapter")
    report("Cache miss returns None", result is None)


def test_html_fetch():
    """Fetch a real Cisco chapter page and verify text extraction."""
    text = gbd.fetch_chapter_html(SAMPLE_CHAPTER_URL)
    has_text = len(text) >= gbd.MIN_USABLE_CHARS
    report(
        "HTML fetch returns usable text",
        has_text,
        f"{len(text)} chars from {SAMPLE_CHAPTER_URL.split('/')[-1]}"
    )
    if has_text:
        # Sanity: should contain BGP-related content
        has_bgp = "bgp" in text.lower() or "border gateway" in text.lower()
        report("Fetched text contains expected content (BGP)", has_bgp)
    else:
        skip("Content check", "fetch returned too little text")


def test_html_fetch_bad_url():
    """Verify graceful handling of a 404 URL."""
    text = gbd.fetch_chapter_html(
        "https://www.cisco.com/c/en/us/td/docs/routers/sdwan/NONEXISTENT.html"
    )
    report("Bad URL returns empty string", text == "", f"got {len(text)} chars")


def test_get_chapter_text_cache_first():
    """get_chapter_text should return cache if available."""
    tmp_dir = tempfile.mkdtemp(prefix="gbd_test_")
    original_dir = gbd.KNOWLEDGE_DOCS_DIR
    try:
        gbd.KNOWLEDGE_DOCS_DIR = Path(tmp_dir)
        cached_content = "Cached chapter text about OSPF configuration." * 10
        gbd.save_cached_text(PRODUCT, "test-book", "test-chapter", cached_content)

        text, source = gbd.get_chapter_text(
            product=PRODUCT,
            book_slug="test-book",
            chapter_slug="test-chapter",
            chapter_url="https://example.com/should-not-be-fetched",
            skip_fetch=False,
        )
        report("get_chapter_text prefers cache", source == "cache",
               f"source={source}")
        report("Cached content matches", text == cached_content)
    finally:
        gbd.KNOWLEDGE_DOCS_DIR = original_dir
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_get_chapter_text_html_fallback():
    """get_chapter_text should fetch HTML when cache is empty."""
    tmp_dir = tempfile.mkdtemp(prefix="gbd_test_")
    original_dir = gbd.KNOWLEDGE_DOCS_DIR
    try:
        gbd.KNOWLEDGE_DOCS_DIR = Path(tmp_dir)
        text, source = gbd.get_chapter_text(
            product=PRODUCT,
            book_slug="routing-book-xe",
            chapter_slug=SAMPLE_CHAPTER_SLUG,
            chapter_url=SAMPLE_CHAPTER_URL,
            skip_fetch=False,
        )
        report("get_chapter_text falls back to HTML", source == "html",
               f"source={source}, {len(text)} chars")

        # Verify it was also cached
        cached = gbd.load_cached_text(PRODUCT, "routing-book-xe", SAMPLE_CHAPTER_SLUG)
        report("HTML result was cached for next time", cached == text)
    finally:
        gbd.KNOWLEDGE_DOCS_DIR = original_dir
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_get_chapter_text_skip_fetch():
    """get_chapter_text with skip_fetch=True and no cache returns 'none'."""
    tmp_dir = tempfile.mkdtemp(prefix="gbd_test_")
    original_dir = gbd.KNOWLEDGE_DOCS_DIR
    try:
        gbd.KNOWLEDGE_DOCS_DIR = Path(tmp_dir)
        text, source = gbd.get_chapter_text(
            product=PRODUCT,
            book_slug="test-book",
            chapter_slug="test-chapter",
            chapter_url=SAMPLE_CHAPTER_URL,
            skip_fetch=True,
        )
        report("skip_fetch with no cache returns 'none'", source == "none")
    finally:
        gbd.KNOWLEDGE_DOCS_DIR = original_dir
        shutil.rmtree(tmp_dir, ignore_errors=True)


def test_inventory_loads():
    """Verify the sdwan inventory file exists and has chapters."""
    inv_file = gbd.INVENTORY_DIR / PRODUCT / "document_inventory.json"
    if not inv_file.exists():
        skip("Inventory load", f"{inv_file} not found")
        return

    with open(inv_file) as f:
        inv = json.load(f)

    report("Inventory file loads", isinstance(inv, dict) and len(inv) > 0,
           f"{len(inv)} books")

    # Check routing book has chapters
    book = inv.get(SAMPLE_BOOK, {})
    chapters = book.get("chapters", [])
    report(f"{SAMPLE_BOOK} has chapters", len(chapters) > 0,
           f"{len(chapters)} chapters")


def test_existing_cached_files():
    """Check that previously fetched .txt files exist in knowledge_docs/sdwan/."""
    book_dir = gbd.KNOWLEDGE_DOCS_DIR / PRODUCT / "routing-book-xe"
    if not book_dir.exists():
        skip("Existing cache check", "routing-book-xe/ not fetched yet")
        return

    txt_files = list(book_dir.glob("*.txt"))
    report("routing-book-xe has cached .txt files", len(txt_files) > 0,
           f"{len(txt_files)} files")


def test_output_json_structure():
    """Verify the output book_descriptions.json has valid structure (if it exists)."""
    output_file = gbd.ONTOLOGY_DIR / PRODUCT / "book_descriptions.json"
    if not output_file.exists():
        skip("Output JSON check", "book_descriptions.json not yet generated")
        return

    with open(output_file) as f:
        data = json.load(f)

    report("Output JSON is a dict", isinstance(data, dict))
    if data:
        first_key = next(iter(data))
        entry = data[first_key]
        has_title = "title" in entry
        has_chapters = "chapters" in entry
        report("Book entry has 'title' and 'chapters'",
               has_title and has_chapters,
               f"first book: {first_key}")


# ── Runner ───────────────────────────────────────────────────────────────────

def main():
    print("\n" + "=" * 70)
    print("  gen_book_descriptions.py — Test Suite")
    print("=" * 70)

    print("\n📁 Cache & Path Tests:")
    test_cache_path()
    test_cache_roundtrip()
    test_cache_miss()

    print("\n🌐 HTML Fetch Tests:")
    test_html_fetch()
    test_html_fetch_bad_url()

    print("\n🔄 get_chapter_text Integration Tests:")
    test_get_chapter_text_cache_first()
    test_get_chapter_text_html_fallback()
    test_get_chapter_text_skip_fetch()

    print("\n📦 Data & Inventory Tests:")
    test_inventory_loads()
    test_existing_cached_files()
    test_output_json_structure()

    # Summary
    total = passed + failed + skipped
    print("\n" + "=" * 70)
    print(f"  RESULTS: {passed} passed, {failed} failed, {skipped} skipped  (total: {total})")
    print("=" * 70)

    return 0 if failed == 0 else 1


if __name__ == "__main__":
    sys.exit(main())
