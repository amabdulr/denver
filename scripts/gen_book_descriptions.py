#!/usr/bin/env python3
"""
gen_book_descriptions.py — Run the kgraph.md AI prompt on every chapter
of every book in a product folder and save RDF triples to the ontology folder.

Strategy  (HTML-only, cached):
  1. Check local text cache  → use it if present
  2. Fetch the chapter HTML page, extract text, cache it locally
  3. Validate the text (min 200 chars) before calling the LLM
  4. Send to LLM with the kgraph.md prompt
  5. Parse pipe-delimited RDF triples from the response
  6. Save after every chapter (crash-safe resume)

Cache lives in  knowledge_docs/<product>/<book-slug>/<chapter-slug>.md  (or .txt legacy)
Once cached, a chapter is never re-fetched.

Usage:
  python scripts/gen_book_descriptions.py                            # sdwan (default)
  python scripts/gen_book_descriptions.py --product 9800             # different product
  python scripts/gen_book_descriptions.py --book routing-book-xe.pdf # single book
  python scripts/gen_book_descriptions.py --model claude-sonnet-4    # different model
  python scripts/gen_book_descriptions.py --fetch-only               # download only, no LLM
  python scripts/gen_book_descriptions.py --dry-run                  # no fetching, no LLM
"""

import argparse
import json
import re
import signal
import sys
import time
from datetime import datetime, timedelta
from pathlib import Path

import requests
from bs4 import BeautifulSoup
from dotenv import load_dotenv

# ── Locate project root and put app/ on path ────────────────────────────────
BASE_DIR = Path(__file__).resolve().parent.parent   # …/Denver2/
sys.path.insert(0, str(BASE_DIR / "app"))

from utils import get_llm, ConfigurationError  # noqa: E402


class TokenExpiredError(Exception):
    """Raised when the BridgeIt auth token has expired (HTTP 401)."""
    pass


def _invalidate_token_cache() -> None:
    """Delete the cached auth token so the next get_llm() call fetches a fresh one."""
    cache_file = BASE_DIR / "data" / "auth_token_cache.json"
    if cache_file.exists():
        cache_file.unlink()
        print("  [token] Invalidated cached auth token")

# ── Paths ────────────────────────────────────────────────────────────────────
INVENTORY_DIR     = BASE_DIR / "inventory"
ONTOLOGY_DIR      = BASE_DIR / "config" / "ontology"
PROMPTS_DIR       = BASE_DIR / "prompts"
PROMPT_FILE        = PROMPTS_DIR / "kgraph.md"
KNOWLEDGE_DOCS_DIR = BASE_DIR / "knowledge_docs"

# ── Defaults ─────────────────────────────────────────────────────────────────
DEFAULT_PRODUCT = "sdwan"
DEFAULT_MODEL   = "claude-sonnet-4"

# ── Tuning ───────────────────────────────────────────────────────────────────
MAX_CONTENT_CHARS    = 50_000  # max chars of chapter text sent to LLM
MIN_USABLE_CHARS     = 200     # text shorter than this is treated as "empty"
MAX_RETRIES          = 4       # LLM / HTTP retries
LLM_TIMEOUT          = 90     # seconds max per LLM call
LLM_DELAY            = 1.0     # seconds between LLM calls
FETCH_DELAY          = 0.5     # seconds between HTTP fetches (rate-limit)
REQUEST_TIMEOUT      = 20      # seconds per HTTP request
HTTP_RETRIES         = 2       # retries for transient HTTP errors


# ── Text cache ───────────────────────────────────────────────────────────────

def _cache_path(product: str, book_slug: str, chapter_slug: str) -> Path:
    md = KNOWLEDGE_DOCS_DIR / product / book_slug / f"{chapter_slug}.md"
    if md.exists():
        return md
    pdf = KNOWLEDGE_DOCS_DIR / product / book_slug / f"{chapter_slug}.pdf"
    if pdf.exists():
        return pdf
    return md  # default to .md for new files


def load_cached_text(product: str, book_slug: str, chapter_slug: str):
    """Return cached text or None."""
    p = _cache_path(product, book_slug, chapter_slug)
    if p.exists():
        return p.read_text(encoding="utf-8")
    return None


def save_cached_text(product: str, book_slug: str, chapter_slug: str, text: str) -> None:
    p = KNOWLEDGE_DOCS_DIR / product / book_slug / f"{chapter_slug}.md"
    p.parent.mkdir(parents=True, exist_ok=True)
    p.write_text(text, encoding="utf-8")


# ── HTML → text ──────────────────────────────────────────────────────────────

def fetch_chapter_html(url: str) -> str:
    """Fetch a chapter HTML page with retries and return extracted plain text."""
    for attempt in range(1, HTTP_RETRIES + 1):
        try:
            resp = requests.get(url, timeout=REQUEST_TIMEOUT)
            if resp.status_code in (401, 403):
                print(f"       [warn] HTTP {resp.status_code} — page may require auth")
                return ""
            if resp.status_code == 404:
                print(f"       [warn] HTTP 404 — page not found")
                return ""
            resp.raise_for_status()

            soup = BeautifulSoup(resp.text, "html.parser")

            # Strip non-content elements
            for tag in soup(["nav", "header", "footer", "script", "style",
                             "aside", "noscript", "iframe"]):
                tag.decompose()

            # Prefer a semantic content container
            main = (
                soup.find("main")
                or soup.find("article")
                or soup.find("div", class_=re.compile(r"\b(content|body|main)\b", re.I))
                or soup.body
            )
            raw = (main or soup).get_text(separator="\n", strip=True)
            lines = [ln for ln in raw.splitlines() if ln.strip()]
            return "\n".join(lines)[:MAX_CONTENT_CHARS]

        except requests.exceptions.Timeout:
            print(f"       [warn] timeout (attempt {attempt}/{HTTP_RETRIES})")
        except requests.exceptions.ConnectionError:
            print(f"       [warn] connection error (attempt {attempt}/{HTTP_RETRIES})")
        except Exception as exc:
            print(f"       [warn] fetch error: {str(exc)[:120]}")
            return ""

        if attempt < HTTP_RETRIES:
            time.sleep(3 * attempt)

    return ""


# ── Content acquisition (cache → HTML) ────────────────────────────────────────

def get_chapter_text(
    product: str,
    book_slug: str,
    chapter_slug: str,
    chapter_url: str,
    skip_fetch: bool = False,
) -> tuple:
    """
    Try in order: local cache → HTML fetch.
    Returns (text, source) where source is 'cache', 'html', or 'none'.
    """
    # 1. Cache hit
    cached = load_cached_text(product, book_slug, chapter_slug)
    if cached and len(cached) >= MIN_USABLE_CHARS:
        return cached, "cache"

    # 2. HTML fetch
    if not skip_fetch and chapter_url:
        html_text = fetch_chapter_html(chapter_url)
        if html_text and len(html_text) >= MIN_USABLE_CHARS:
            save_cached_text(product, book_slug, chapter_slug, html_text)
            return html_text, "html"

    return "", "none"


# ── LLM call ─────────────────────────────────────────────────────────────────

# Header row for the RDF triples CSV
_RDF_HEADER = "Subject|Predicate|Object|CategoryType|SourceTrace"


def _parse_rdf_triples(raw: str) -> list[str]:
    """
    Extract pipe-delimited RDF triple lines from the LLM response.
    Returns a list of raw triple strings (without the header row).
    """
    lines = []
    in_code_block = False
    for line in raw.splitlines():
        stripped = line.strip()
        if stripped.startswith("```"):
            in_code_block = not in_code_block
            continue
        # Accept lines with exactly 4 pipe separators (5 columns)
        if stripped.count("|") >= 4 and not stripped.lower().startswith("subject|"):
            lines.append(stripped)
    return lines


def call_llm(prompt_template: str, book_title: str,
             chapter_title: str, chapter_text: str, llm) -> dict:
    """
    Compose a message from the kgraph prompt + chapter context, invoke the LLM,
    and return a dict with 'triples' (list of pipe-delimited strings) and 'raw'.
    """
    content_block = chapter_text if chapter_text else "(Content not available — use the chapter title.)"

    message = (
        f"{prompt_template}\n\n"
        "---\n\n"
        "Now extract RDF triples for the following chapter.\n\n"
        f"**Book:** {book_title}\n"
        f"**Chapter:** {chapter_title}\n\n"
        f"**Content (excerpt):**\n{content_block}"
    )

    def _timeout_handler(signum, frame):
        raise TimeoutError("LLM call exceeded timeout")

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            old_handler = signal.signal(signal.SIGALRM, _timeout_handler)
            signal.alarm(LLM_TIMEOUT)
            try:
                response = llm.invoke(message)
            finally:
                signal.alarm(0)
                signal.signal(signal.SIGALRM, old_handler)

            raw = response.content.strip()
            triples = _parse_rdf_triples(raw)
            return {"triples": triples, "raw": raw}

        except TimeoutError:
            print(f"    [warn] LLM attempt {attempt}/{MAX_RETRIES} timed out ({LLM_TIMEOUT}s)")
            if attempt < MAX_RETRIES:
                time.sleep(3)
        except Exception as exc:
            err = str(exc)[:200]
            if "401" in err or "TokenExpired" in err:
                print(f"    [warn] Auth token expired — need refresh")
                raise TokenExpiredError(err)
            print(f"    [warn] LLM attempt {attempt}/{MAX_RETRIES} failed: {err}")
            if attempt < MAX_RETRIES:
                time.sleep(5)

    return {"triples": [], "raw": ""}


# ── Persistence helpers ───────────────────────────────────────────────────────

def load_results(path: Path) -> dict:
    if path.exists():
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_results(path: Path, data: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2, ensure_ascii=False)


# ── Main ──────────────────────────────────────────────────────────────────────

def main() -> None:
    ap = argparse.ArgumentParser(
        description="Run kgraph.md prompt on every chapter and save RDF triples to ontology folder.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog=__doc__,
    )
    ap.add_argument("--product",    default=DEFAULT_PRODUCT,
                    help=f"Product sub-folder under inventory/ (default: {DEFAULT_PRODUCT})")
    ap.add_argument("--book",       default=None,
                    help="Process only this book filename (e.g. routing-book-xe.pdf)")
    ap.add_argument("--model",      default=DEFAULT_MODEL,
                    help=f"LLM model name (default: {DEFAULT_MODEL})")
    ap.add_argument("--fetch-only", action="store_true",
                    help="Download & cache all chapter text (no LLM calls)")
    ap.add_argument("--dry-run",    action="store_true",
                    help="Do not fetch or call the LLM; just list what would be processed")
    ap.add_argument("--progress",   action="store_true",
                    help="Show detailed progress with timestamps and ETA")
    args = ap.parse_args()

    # Default --progress to True so you always see what's happening
    show_progress = True

    load_dotenv(BASE_DIR / ".env")

    # ── Prompt ────────────────────────────────────────────────────────────────
    if not PROMPT_FILE.exists():
        print(f"[error] Prompt file not found: {PROMPT_FILE}")
        sys.exit(1)
    prompt_template = PROMPT_FILE.read_text(encoding="utf-8")
    print(f"Prompt   : {PROMPT_FILE.name}  ({len(prompt_template):,} chars)")

    # ── Inventory ─────────────────────────────────────────────────────────────
    inventory_file = INVENTORY_DIR / args.product / "document_inventory.json"
    if not inventory_file.exists():
        print(f"[error] Inventory not found: {inventory_file}")
        sys.exit(1)
    with open(inventory_file, encoding="utf-8") as fh:
        inventory: dict = json.load(fh)
    print(f"Inventory: {inventory_file}  ({len(inventory)} books)")

    if args.book:
        if args.book not in inventory:
            print(f"[error] Book '{args.book}' not in inventory")
            sys.exit(1)
        inventory = {args.book: inventory[args.book]}

    # ── Output file ───────────────────────────────────────────────────────────
    output_file = ONTOLOGY_DIR / args.product / "book_kgraph.json"
    results = load_results(output_file)
    print(f"Output   : {output_file}")
    print(f"Cache    : {KNOWLEDGE_DOCS_DIR / args.product}")
    if results:
        already = sum(
            len(b.get("chapters", {}))
            for b in results.values()
            if isinstance(b, dict)
        )
        print(f"  Resuming — {len(results)} books / {already} chapters already done")

    # ── LLM ──────────────────────────────────────────────────────────────────
    llm = None
    if not args.dry_run and not args.fetch_only:
        try:
            llm = get_llm(model_name=args.model)
            print(f"LLM      : {args.model}")
        except ConfigurationError as exc:
            print(f"[error] {exc}")
            sys.exit(1)

    # ── Counters ─────────────────────────────────────────────────────────────
    n_books   = len(inventory)
    total_new = 0
    total_triples = 0
    stats     = {"cache": 0, "html": 0, "none": 0}

    # Count total chapters for progress tracking
    total_chapters = sum(len(b.get("chapters", [])) for b in inventory.values())
    already_done = sum(
        1
        for b in results.values() if isinstance(b, dict)
        for c in b.get("chapters", {}).values()
        if "triples" in c
    )
    chapters_to_process = total_chapters - already_done
    run_start = time.time()
    llm_calls = 0  # count of actual LLM calls this session

    if show_progress:
        print(f"\n{'='*60}")
        print(f"  PROGRESS: {total_chapters} total chapters, {already_done} already done, {chapters_to_process} remaining")
        print(f"  Started : {datetime.now().strftime('%H:%M:%S')}")
        print(f"{'='*60}")

    # ── Processing ────────────────────────────────────────────────────────────
    for bi, (filename, book_data) in enumerate(inventory.items(), 1):
        book_title = book_data.get("title", filename)
        chapters   = book_data.get("chapters", [])
        book_slug  = filename.replace(".pdf", "")

        print(f"\n[{bi}/{n_books}] {filename}")
        print(f"  {book_title}")
        print(f"  {len(chapters)} chapter(s)")

        if not chapters:
            print("  (no chapters in inventory — skipping)")
            continue

        # Initialise or carry forward existing book entry
        if filename not in results:
            results[filename] = {"title": book_title, "chapters": {}}

        book_chapters: dict = results[filename].setdefault("chapters", {})
        new_this_book = 0

        for ch in chapters:
            slug      = ch.get("chapter_slug", "")
            ch_title  = ch.get("chapter_title", "")
            ch_url    = ch.get("chapter_url", "")

            if not slug:
                continue

            # Skip if already processed during a previous run (unless fetch-only)
            existing = book_chapters.get(slug, {})
            if not args.fetch_only and "triples" in existing:
                continue

            print(f"  → {ch_title}")

            # ── Dry-run: just list ────────────────────────────────────────────
            if args.dry_run:
                cached = load_cached_text(args.product, book_slug, slug)
                tag = "cached" if cached else "pending"
                book_chapters[slug] = {
                    "title": ch_title,
                    "url":   ch_url,
                    "triples": [f"[dry-run — {tag}]"],
                }
                new_this_book += 1
                total_new += 1
                continue

            # ── Get chapter text (cache → HTML) ──────────────────────────────
            ch_text, source = get_chapter_text(
                product=args.product,
                book_slug=book_slug,
                chapter_slug=slug,
                chapter_url=ch_url,
                skip_fetch=False,
            )
            stats[source] += 1
            print(f"       [{source}] {len(ch_text):,} chars")

            if source == "html":
                time.sleep(FETCH_DELAY)  # rate-limit web requests

            # ── Fetch-only: stop here ─────────────────────────────────────────
            if args.fetch_only:
                new_this_book += 1
                total_new += 1
                continue

            # ── Validate before LLM ───────────────────────────────────────────
            if len(ch_text) < MIN_USABLE_CHARS:
                print(f"       [skip] text too short ({len(ch_text)} chars) — using title only")

            # ── Call LLM ──────────────────────────────────────────────────────
            llm_start = time.time()
            try:
                result = call_llm(
                    prompt_template, book_title, ch_title, ch_text, llm
                )
            except TokenExpiredError:
                # Refresh the token and retry this chapter
                _invalidate_token_cache()
                try:
                    llm = get_llm(model_name=args.model)
                    print("  [token] Refreshed LLM auth token")
                    result = call_llm(
                        prompt_template, book_title, ch_title, ch_text, llm
                    )
                except Exception as exc:
                    print(f"  [error] Token refresh failed: {str(exc)[:200]}")
                    result = {"triples": [], "raw": ""}
            llm_elapsed = time.time() - llm_start
            llm_calls += 1

            book_chapters[slug] = {
                "title": ch_title,
                "url":   ch_url,
                "source": source,
                "triples": result["triples"],
            }
            n_triples = len(result['triples'])
            total_triples += n_triples
            new_this_book += 1
            total_new += 1

            # ── Progress display ──────────────────────────────────────────────
            if show_progress:
                elapsed = time.time() - run_start
                avg_per_ch = elapsed / llm_calls if llm_calls else 0
                remaining_ch = chapters_to_process - total_new
                eta_secs = avg_per_ch * remaining_ch
                eta_str = str(timedelta(seconds=int(eta_secs)))
                elapsed_str = str(timedelta(seconds=int(elapsed)))
                now_str = datetime.now().strftime('%H:%M:%S')
                print(f"       {n_triples} triples ({llm_elapsed:.1f}s)  |  "
                      f"[{now_str}] {total_new}/{chapters_to_process} done  |  "
                      f"elapsed {elapsed_str}  |  ETA {eta_str}  |  "
                      f"total triples: {total_triples:,}")
            else:
                print(f"       {n_triples} triples extracted")

            # Persist after every chapter (crash-safe resume)
            save_results(output_file, results)

            time.sleep(LLM_DELAY)

        print(f"  Done: {new_this_book} new chapter(s) processed")

    # Final save
    if not args.fetch_only:
        save_results(output_file, results)

    # ── Summary ───────────────────────────────────────────────────────────────
    elapsed = time.time() - run_start
    elapsed_str = str(timedelta(seconds=int(elapsed)))
    mode = "(dry-run) " if args.dry_run else "(fetch-only) " if args.fetch_only else ""
    print(f"\n{'='*60}")
    print(f"  {mode}DONE  —  {datetime.now().strftime('%H:%M:%S')}")
    print(f"  {total_new} chapter(s) processed across {n_books} book(s) in {elapsed_str}")
    print(f"  Total triples extracted: {total_triples:,}")
    print(f"  Sources: {stats['cache']} cache, {stats['html']} html, {stats['none']} empty")
    if llm_calls:
        print(f"  Avg time per chapter: {elapsed/llm_calls:.1f}s")
    if not args.fetch_only:
        print(f"  Saved to: {output_file}")
    print(f"{'='*60}")


if __name__ == "__main__":
    main()
