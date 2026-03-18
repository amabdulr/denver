#!/usr/bin/env python3
"""
Extract chapters from systems-interfaces-book-xe-sdwan.pdf into .txt files.

This book's HTML pages on cisco.com are JavaScript-rendered (Adobe AEM),
so the regular HTML fetch returns only a shell.  This script extracts text
from the local PDF using bookmark page ranges and saves each chapter to
  knowledge_docs/sdwan/systems-interfaces-book-xe-sdwan/<chapter-slug>.txt

Usage:
    python scripts/extract_systems_interfaces_pdf.py          # run extraction
    python scripts/extract_systems_interfaces_pdf.py --dry-run # preview only
"""
import argparse
import json
import re
from pathlib import Path

from pypdf import PdfReader

BASE_DIR = Path(__file__).resolve().parent.parent
PDF_PATH = BASE_DIR / "pdf_archive" / "sdwan" / "systems-interfaces-book-xe-sdwan.pdf"
INVENTORY = BASE_DIR / "inventory" / "sdwan" / "document_inventory.json"
OUTPUT_DIR = BASE_DIR / "knowledge_docs" / "sdwan" / "systems-interfaces-book-xe-sdwan"
BOOK_KEY = "systems-interfaces-book-xe-sdwan.pdf"

MAX_CHARS = 8_000          # match the main script's cap
MIN_USABLE_CHARS = 200     # skip trivially short chapters


def _get_top_level_bookmarks(reader: PdfReader) -> list[dict]:
    """Return [{"title": ..., "page": page_number}, ...] for top-level bookmarks."""
    results = []
    for item in reader.outline:
        if isinstance(item, list):
            continue  # skip nested bookmarks
        page_num = reader.get_destination_page_number(item)
        results.append({"title": item.title, "page": page_num})
    return results


def _extract_pages(reader: PdfReader, start: int, end: int) -> str:
    """Extract and join text from pages [start, end)."""
    parts = []
    for i in range(start, min(end, len(reader.pages))):
        text = reader.pages[i].extract_text() or ""
        parts.append(text)
    raw = "\n".join(parts)
    # Clean up: collapse excessive whitespace, strip header/footer noise
    lines = [ln.strip() for ln in raw.splitlines() if ln.strip()]
    return "\n".join(lines)[:MAX_CHARS]


def _match_slug(bookmark_title: str, chapters: list, used: set):
    """Fuzzy-match a bookmark title to an inventory chapter slug (skip already-used)."""
    norm = bookmark_title.strip().lower()
    # Normalise multi-line chapter titles for comparison
    def _norm(t):
        return " ".join(t.split()).lower()

    # Pass 1: exact title match
    for ch in chapters:
        s = ch["chapter_slug"]
        if s in used:
            continue
        if _norm(ch["chapter_title"]) == _norm(bookmark_title):
            return s
    # Pass 2: substring match
    for ch in chapters:
        s = ch["chapter_slug"]
        if s in used:
            continue
        ct = _norm(ch["chapter_title"])
        if norm in ct or ct in norm:
            return s
    return None


def main():
    ap = argparse.ArgumentParser(description=__doc__)
    ap.add_argument("--dry-run", action="store_true",
                    help="Preview bookmark→chapter mapping without writing files")
    args = ap.parse_args()

    # ── Load inventory chapters ──────────────────────────────────────────────
    with open(INVENTORY, encoding="utf-8") as fh:
        inv = json.load(fh)
    chapters = inv[BOOK_KEY]["chapters"]
    slug_set = {ch["chapter_slug"] for ch in chapters}
    print(f"Inventory : {len(chapters)} chapters")

    # ── Read PDF ─────────────────────────────────────────────────────────────
    reader = PdfReader(str(PDF_PATH))
    print(f"PDF       : {PDF_PATH.name}  ({len(reader.pages)} pages)")

    bookmarks = _get_top_level_bookmarks(reader)
    print(f"Bookmarks : {len(bookmarks)} top-level entries")

    OUTPUT_DIR.mkdir(parents=True, exist_ok=True)
    print(f"Output    : {OUTPUT_DIR}\n")

    # ── Process each bookmark ────────────────────────────────────────────────
    matched = 0
    skipped = 0
    written = 0
    used_slugs = set()

    for idx, bm in enumerate(bookmarks):
        # Page range: from this bookmark to the next one (or end of PDF)
        start_page = bm["page"]
        end_page = bookmarks[idx + 1]["page"] if idx + 1 < len(bookmarks) else len(reader.pages)

        slug = _match_slug(bm["title"], chapters, used_slugs)
        pages_str = f"pp {start_page + 1}-{end_page}"

        if not slug:
            print(f"  [{idx + 1:2d}] SKIP  {bm['title'][:70]}  — no inventory match")
            skipped += 1
            continue

        used_slugs.add(slug)
        matched += 1
        text = _extract_pages(reader, start_page, end_page)

        if args.dry_run:
            print(f"  [{idx + 1:2d}] {slug}  ({len(text):,} chars, {pages_str})")
            continue

        if len(text) < MIN_USABLE_CHARS:
            print(f"  [{idx + 1:2d}] {slug}  — too short ({len(text)} chars), skipping")
            continue

        out_file = OUTPUT_DIR / f"{slug}.txt"
        out_file.write_text(text, encoding="utf-8")
        written += 1
        print(f"  [{idx + 1:2d}] {slug}  ({len(text):,} chars) → saved")

    # ── Summary ──────────────────────────────────────────────────────────────
    print(f"\nDone: {matched} matched, {written} written, {skipped} unmatched")
    remaining = slug_set - used_slugs
    if remaining:
        print(f"Inventory chapters with no bookmark match ({len(remaining)}):")
        for s in sorted(remaining):
            print(f"  - {s}")


if __name__ == "__main__":
    main()
