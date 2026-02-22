#!/usr/bin/env python3
"""
scour_books.py  — Scour PDF guide TOCs and generate concept-to-guide mappings.

Strategy:
  1. Extract TOC from each PDF (bookmarks first, fallback to first-pages text scan)
  2. Send each book's headings to an LLM for concept/synonym extraction
  3. Cross-reference against networking_terms.json vocabulary
  4. Output draft mappings + gap report (new terms not yet in vocabulary)

Usage:
  python scour_books.py                           # All products, default model
  python scour_books.py --product sdwan            # One product only
  python scour_books.py --model gpt-4.1            # Different model
  python scour_books.py --book routing-book-xe.pdf # Single book
  python scour_books.py --dry-run                  # Extract TOCs only, no LLM
"""

import argparse
import json
import os
import re
import sys
import time
from pathlib import Path
from typing import Optional

from dotenv import load_dotenv
from pypdf import PdfReader

# ── Setup ──────────────────────────────────────────────────────────────────

BASE_DIR = Path(__file__).parent
KNOWLEDGE_DIR = BASE_DIR / "knowledge_docs"
TERMS_FILE = BASE_DIR / "networking_terms.json"
MAPPINGS_FILE = BASE_DIR / "guide_mappings.json"
OUTPUT_DIR = BASE_DIR / "scour_output"

# Max headings per LLM call. Books with more get chunked.
CHUNK_SIZE = 300
CHUNK_OVERLAP = 20  # overlap so we don't lose context at boundaries

# ── TOC Extraction ─────────────────────────────────────────────────────────

def extract_bookmarks(pdf_path: Path, max_depth: int = 3) -> list[str]:
    """
    Extract bookmark/outline headings from a PDF (Method A).
    Returns flat list of heading strings, up to max_depth levels deep.
    """
    try:
        reader = PdfReader(str(pdf_path))
        outline = reader.outline
        if not outline:
            return []
    except Exception:
        return []

    headings = []

    def walk(items, depth=0):
        if depth >= max_depth:
            return
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
            elif hasattr(item, "title"):
                title = item.title.strip()
                if title:
                    headings.append(title)

    walk(outline)
    return headings


def extract_toc_from_text(pdf_path: Path, max_pages: int = 12) -> list[str]:
    """
    Fallback: extract TOC-looking lines from the first N pages (Method B).
    Looks for patterns like "Chapter 5: Configure BGP ... 45" or
    "Configure Multicast .............. 123"
    """
    try:
        reader = PdfReader(str(pdf_path))
    except Exception:
        return []

    raw_text = ""
    for i, page in enumerate(reader.pages):
        if i >= max_pages:
            break
        text = page.extract_text()
        if text:
            raw_text += text + "\n"

    if not raw_text:
        return []

    headings = []
    # Patterns that indicate TOC lines
    toc_patterns = [
        # "Chapter N: Title ... page"
        re.compile(r"(?:chapter|part|section)\s*\d+[:\.\s]+(.+?)(?:\s*\.{2,}\s*\d+|\s+\d+\s*$)", re.IGNORECASE),
        # "Title ........... page"
        re.compile(r"^(.{10,80}?)\s*\.{3,}\s*\d+", re.MULTILINE),
        # "Title    123"  (tab-separated or multi-space)
        re.compile(r"^(.{10,80}?)\s{3,}\d{1,4}\s*$", re.MULTILINE),
    ]

    for pattern in toc_patterns:
        for match in pattern.finditer(raw_text):
            heading = match.group(1).strip()
            # Skip obviously non-TOC lines
            if len(heading) < 5 or len(heading) > 120:
                continue
            if heading.lower().startswith(("page", "table", "figure", "©", "cisco")):
                continue
            headings.append(heading)

    # Deduplicate while preserving order
    seen = set()
    unique = []
    for h in headings:
        key = h.lower().strip()
        if key not in seen:
            seen.add(key)
            unique.append(h)

    return unique


def extract_toc(pdf_path: Path) -> tuple[list[str], str]:
    """
    Try bookmarks first, fallback to text scan.
    Returns (headings, method_used).
    """
    headings = extract_bookmarks(pdf_path)
    if headings:
        return headings, "bookmarks"

    headings = extract_toc_from_text(pdf_path)
    if headings:
        return headings, "text_scan"

    return [], "none"


# ── Vocabulary Loading ─────────────────────────────────────────────────────

def load_vocabulary() -> set[str]:
    """Load all terms from networking_terms.json into a flat set (lowercase)."""
    with open(TERMS_FILE) as f:
        data = json.load(f)

    terms = set()
    for key, value in data.items():
        if key.startswith("_"):
            continue
        if isinstance(value, list):
            for t in value:
                terms.add(t.lower().strip())
    return terms


def load_existing_mappings() -> dict:
    """Load current concept_to_guide from guide_mappings.json."""
    with open(MAPPINGS_FILE) as f:
        data = json.load(f)
    return {k: v for k, v in data.get("concept_to_guide", {}).items()
            if not k.startswith("_")}


# ── LLM Concept Extraction ────────────────────────────────────────────────

LLM_PROMPT = """\
You are a Cisco networking documentation expert. I am building a system that \
maps networking concepts to documentation guide filenames so that when an \
engineer files a bug mentioning a concept, the correct guide is auto-selected.

Below are the TABLE OF CONTENTS headings from a Cisco documentation PDF.

**Book filename:** {filename}
**Product family:** {product}

**Headings:**
{headings}

Your task:
1. For each meaningful heading/section, extract the **networking concepts** it covers.
2. For each concept, also list **synonyms and abbreviations** that a Cisco engineer \
might use when describing a bug related to that topic. Think about:
   - Acronyms (e.g., "Bidirectional Forwarding Detection" → "bfd")
   - Short forms (e.g., "route leaking" → "route leak")
   - Related sub-concepts (e.g., a "Multicast" chapter likely covers "pim", "igmp", "msdp", "rendezvous point")
   - How engineers actually describe problems in bug reports (e.g., "routes not showing up" → "route redistribution")
3. For each concept/synonym, provide the **filename pattern** — a short substring \
that would match this book's filename. Use the part of the filename that is most \
distinctive (e.g., for "routing-book-xe.pdf" use "routing"; for "b-multicast-cg-asr9k-25xx.pdf" use "multicast").

**Output format:** Return a JSON object where:
- Keys are lowercase concept/synonym strings (what an engineer would type in a bug)
- Values are arrays of filename pattern substrings that should match this book

Example output:
```json
{{
  "bgp": ["routing"],
  "border gateway protocol": ["routing"],
  "ospf": ["routing"],
  "route redistribution": ["routing"],
  "pim": ["routing", "multicast"],
  "igmp": ["routing", "multicast"]
}}
```

Rules:
- Keys must be lowercase
- Keep filename patterns short (one distinctive word/hyphenated-segment from the filename)
- Include BOTH the full concept name AND common abbreviations as separate keys
- Skip generic headings like "Overview", "Prerequisites", "Feature History", "References"
- For chapters that cover configuration, include the protocol/feature name, NOT "configure" or "configuration"
- If a heading mentions troubleshooting a specific feature, map it to that feature, not to "troubleshooting" generically
- Be thorough — it's better to have too many mappings than too few

Return ONLY the JSON object, no other text.
"""


MAX_RETRIES = 3        # retry on timeout / parse failure
LLM_TIMEOUT = 180      # seconds per LLM call

# Sentinel to signal that the auth token expired and LLM needs refresh
TOKEN_EXPIRED = "__TOKEN_EXPIRED__"


def _try_parse_json(content: str) -> Optional[dict]:
    """
    Try to parse JSON, with fallback repair for truncated responses.
    LLMs sometimes return JSON that's cut off at the end.
    """
    # Strip markdown code fence if present
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```\s*$", "", content)

    # Attempt 1: direct parse
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass

    # Attempt 2: truncated JSON repair — find last complete key-value pair
    # Look for the last "]" that closes a value array, then close the object
    last_bracket = content.rfind("]")
    if last_bracket > 0:
        repaired = content[:last_bracket + 1]
        # Remove any trailing comma
        repaired = repaired.rstrip().rstrip(",")
        repaired += "\n}"
        try:
            result = json.loads(repaired)
            print(f"    🔧 Repaired truncated JSON (recovered up to char {last_bracket})")
            return result
        except json.JSONDecodeError:
            pass

    return None


def get_llm_concepts(
    filename: str,
    product: str,
    headings: list[str],
    llm,
) -> dict[str, list[str]]:
    """
    Send TOC headings to LLM and get concept-to-pattern mappings.
    Returns dict like {"bgp": ["routing"], "ospf": ["routing"], ...}
    Retries on timeout or parse failure.
    """
    headings_text = "\n".join(f"  - {h}" for h in headings)

    prompt = LLM_PROMPT.format(
        filename=filename,
        product=product,
        headings=headings_text,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = llm.invoke(prompt)
            content = response.content.strip()

            result = _try_parse_json(content)

            if result is None:
                print(f"    ⚠ JSON parse failed (attempt {attempt}/{MAX_RETRIES})")
                print(f"    Raw response (first 500 chars): {content[:500]}")
                if attempt < MAX_RETRIES:
                    print(f"    Retrying in 5s...")
                    time.sleep(5)
                    continue
                return {}

            # Validate structure
            if not isinstance(result, dict):
                print(f"    ⚠ LLM returned non-dict type: {type(result)}")
                return {}

            # Ensure all values are lists of strings, all keys lowercase
            cleaned = {}
            for k, v in result.items():
                key = k.lower().strip()
                if not key:
                    continue
                if isinstance(v, list):
                    cleaned[key] = [str(p).lower().strip() for p in v if p]
                elif isinstance(v, str):
                    cleaned[key] = [v.lower().strip()]
            return cleaned

        except Exception as e:
            err = str(e)[:200]
            print(f"    ⚠ LLM error (attempt {attempt}/{MAX_RETRIES}): {err}")
            # Detect auth token expiration — signal caller to refresh LLM
            if "401" in str(e) or "TokenExpired" in str(e) or "token" in str(e).lower():
                print(f"    🔑 Auth token likely expired — signaling refresh")
                return TOKEN_EXPIRED
            if attempt < MAX_RETRIES:
                print(f"    Retrying in 10s...")
                time.sleep(10)
            else:
                return {}

    return {}


# ── Mechanical Matching (no-LLM fallback) ─────────────────────────────────

STRIP_PREFIXES = re.compile(
    r"^(?:chapter|part|section|appendix)\s*\d*[:\.\s]*",
    re.IGNORECASE,
)
STRIP_VERBS = re.compile(
    r"^(?:configure|configuring|verify|verifying|troubleshoot|troubleshooting|"
    r"monitor|monitoring|information about|understanding|overview of|"
    r"restrictions for|prerequisites for|feature history for)\s+",
    re.IGNORECASE,
)
STRIP_SUFFIXES = re.compile(
    r"\s+(?:overview|restrictions|prerequisites|feature history|"
    r"configuration examples?|on wan edge|on service vpn|"
    r"for sd-wan|for cisco ios xe|for cisco ios xr|"
    r"cisco catalyst|cisco ios)\s*$",
    re.IGNORECASE,
)


def normalize_heading(heading: str) -> str:
    """Strip boilerplate from a heading to get the core concept."""
    h = heading.strip()
    h = STRIP_PREFIXES.sub("", h)
    h = STRIP_VERBS.sub("", h)
    h = STRIP_SUFFIXES.sub("", h)
    h = h.strip(" :-–—")
    return h.lower()


def mechanical_match(headings: list[str], vocab: set[str]) -> dict[str, bool]:
    """
    Match heading text against known vocabulary.
    Returns {term: True} for each vocab term found in any heading.
    """
    matches = {}
    all_text = " ".join(normalize_heading(h) for h in headings)

    for term in vocab:
        # Word-boundary match to avoid "nat" matching "destination"
        pattern = r"\b" + re.escape(term) + r"\b"
        if re.search(pattern, all_text, re.IGNORECASE):
            matches[term] = True

    return matches


# ── Filename Pattern Extraction ────────────────────────────────────────────

def derive_book_pattern(filename: str) -> str:
    """
    Extract the most distinctive substring from a guide filename.
    "routing-book-xe.pdf" → "routing"
    "b-multicast-cg-asr9k-25xx.pdf" → "multicast"
    "monitor-maintain-book-xe-sdwan.pdf" → "monitor"
    """
    name = filename.lower().replace(".pdf", "")
    # Remove common prefixes/suffixes
    noise = [
        "b-", "-cg", "-config", "-configuration",
        "-asr9000", "-asr9k", "-cisco8000", "-cisco8k",
        "-25xx", "-r25xx", "-ios-xr", "-8000",
        "-book-xe", "-xe-sdwan", "-sdwan", "-xe",
    ]
    clean = name
    for n in noise:
        clean = clean.replace(n, " ")

    # Split and take the most meaningful segment
    parts = [p.strip() for p in re.split(r"[\s\-_]+", clean) if p.strip()]
    # Filter out very short or generic parts
    generic = {"b", "cg", "config", "guide", "cisco", "book", "xe", "xr", "ios"}
    meaningful = [p for p in parts if p not in generic and len(p) > 1]

    if meaningful:
        return meaningful[0]
    return parts[0] if parts else name


# ── Main Processing ────────────────────────────────────────────────────────

def process_book(
    pdf_path: Path,
    product: str,
    llm,
    vocab: set[str],
    dry_run: bool = False,
) -> dict:
    """
    Process a single PDF:
      1. Extract TOC
      2. Run LLM concept extraction (or mechanical if dry-run)
      3. Return results dict
    """
    filename = pdf_path.name
    short = filename.replace(".pdf", "")

    print(f"\n  📖 {filename}")

    # Step 1: Extract TOC
    headings, method = extract_toc(pdf_path)
    print(f"     TOC method: {method}, headings found: {len(headings)}")

    if not headings:
        print(f"     ⚠ No TOC extracted — skipping")
        return {
            "filename": filename,
            "product": product,
            "toc_method": "none",
            "headings_count": 0,
            "headings": [],
            "concepts": {},
            "mechanical_matches": {},
            "status": "no_toc",
        }

    # Show first few headings
    for h in headings[:5]:
        print(f"       • {h[:80]}")
    if len(headings) > 5:
        print(f"       ... and {len(headings) - 5} more")

    # Step 2: Mechanical vocabulary matching (always)
    mech = mechanical_match(headings, vocab)
    print(f"     Mechanical vocab matches: {len(mech)}")

    # Step 3: LLM concept extraction (unless dry-run)
    concepts = {}
    if not dry_run and llm:
        if len(headings) <= CHUNK_SIZE:
            print(f"     🤖 Querying LLM...")
            concepts = get_llm_concepts(filename, product, headings, llm)
            if concepts == TOKEN_EXPIRED:
                return TOKEN_EXPIRED
            print(f"     LLM concepts returned: {len(concepts)}")
        else:
            # Chunk large books into multiple LLM calls
            chunks = []
            start = 0
            while start < len(headings):
                end = min(start + CHUNK_SIZE, len(headings))
                chunks.append(headings[start:end])
                start = end - CHUNK_OVERLAP  # overlap for context continuity
                if start + CHUNK_OVERLAP >= len(headings):
                    break
            print(f"     🤖 Large book — splitting into {len(chunks)} chunks of ~{CHUNK_SIZE} headings")
            for ci, chunk in enumerate(chunks, 1):
                print(f"        Chunk {ci}/{len(chunks)} ({len(chunk)} headings)...")
                chunk_concepts = get_llm_concepts(filename, product, chunk, llm)
                if chunk_concepts == TOKEN_EXPIRED:
                    return TOKEN_EXPIRED
                # Merge: union of patterns per concept
                for k, v in chunk_concepts.items():
                    if k in concepts:
                        merged = set(concepts[k]) | set(v)
                        concepts[k] = sorted(merged)
                    else:
                        concepts[k] = v
                if ci < len(chunks):
                    time.sleep(1)  # pause between chunks
            print(f"     LLM concepts returned: {len(concepts)} (merged from {len(chunks)} chunks)")
    elif dry_run:
        print(f"     (dry-run — skipping LLM)")

    return {
        "filename": filename,
        "product": product,
        "toc_method": method,
        "headings_count": len(headings),
        "headings": headings,
        "concepts": concepts,
        "mechanical_matches": mech,
        "status": "ok",
    }


def merge_results(
    all_results: list[dict],
    existing_mappings: dict,
    vocab: set[str],
) -> tuple[dict, dict, list[str]]:
    """
    Merge all per-book results into:
      1. draft_mappings: concept → list of filename patterns (union of new + existing)
      2. new_terms: concepts from LLM that aren't in our vocabulary yet
      3. failures: list of filenames where TOC extraction failed
    """
    draft = {}  # concept → set of patterns
    new_terms_map = {}  # term → set of patterns (terms NOT in vocab)
    failures = []

    for result in all_results:
        if result["status"] == "no_toc":
            failures.append(result["filename"])
            continue

        book_pattern = derive_book_pattern(result["filename"])

        # From LLM concepts
        for concept, patterns in result["concepts"].items():
            concept = concept.lower().strip()
            if not concept:
                continue

            # Use LLM-provided patterns, but always include the book pattern too
            all_patterns = set(patterns)
            all_patterns.add(book_pattern)

            if concept in vocab:
                if concept not in draft:
                    draft[concept] = set()
                draft[concept].update(all_patterns)
            else:
                if concept not in new_terms_map:
                    new_terms_map[concept] = set()
                new_terms_map[concept].update(all_patterns)

        # From mechanical matches (always add with book pattern)
        for term in result["mechanical_matches"]:
            if term not in draft:
                draft[term] = set()
            draft[term].add(book_pattern)

    # Merge with existing mappings (union)
    for concept, patterns in existing_mappings.items():
        if concept not in draft:
            draft[concept] = set(patterns)
        else:
            draft[concept].update(patterns)

    # Convert sets to sorted lists
    final_draft = {k: sorted(v) for k, v in sorted(draft.items())}
    final_new = {k: sorted(v) for k, v in sorted(new_terms_map.items())}

    return final_draft, final_new, failures


# ── Output ─────────────────────────────────────────────────────────────────

def save_outputs(
    draft_mappings: dict,
    new_terms: dict,
    failures: list[str],
    all_results: list[dict],
    output_dir: Path,
):
    """Save all outputs to the scour_output directory."""
    output_dir.mkdir(exist_ok=True)

    # 1. Draft concept-to-guide mappings (ready to merge into guide_mappings.json)
    draft_path = output_dir / "draft_concept_mappings.json"
    with open(draft_path, "w") as f:
        json.dump(draft_mappings, f, indent=4)
    print(f"\n✅ Draft mappings: {draft_path}  ({len(draft_mappings)} concepts)")

    # 2. Gap report — new terms found by LLM but not in vocabulary
    gap_path = output_dir / "gap_report_new_terms.json"
    with open(gap_path, "w") as f:
        json.dump(new_terms, f, indent=4)
    print(f"✅ Gap report:     {gap_path}  ({len(new_terms)} new terms)")

    # 3. Failures
    if failures:
        fail_path = output_dir / "failures.txt"
        with open(fail_path, "w") as f:
            f.write("Books where TOC extraction failed:\n")
            for fn in failures:
                f.write(f"  - {fn}\n")
        print(f"⚠️  Failures:      {fail_path}  ({len(failures)} books)")

    # 4. Full raw results (for debugging / review)
    raw_path = output_dir / "raw_results.json"
    # Convert sets in results (headings is fine, but mechanical_matches needs conversion)
    serializable = []
    for r in all_results:
        sr = dict(r)
        sr["mechanical_matches"] = list(sr.get("mechanical_matches", {}).keys())
        serializable.append(sr)
    with open(raw_path, "w") as f:
        json.dump(serializable, f, indent=2)
    print(f"📋 Raw results:   {raw_path}")

    # 5. Human-readable summary
    summary_path = output_dir / "summary.txt"
    with open(summary_path, "w") as f:
        f.write("=" * 70 + "\n")
        f.write("SCOUR BOOKS — SUMMARY\n")
        f.write("=" * 70 + "\n\n")

        total_books = len(all_results)
        ok_books = sum(1 for r in all_results if r["status"] == "ok")
        total_headings = sum(r["headings_count"] for r in all_results)
        total_llm_concepts = sum(len(r["concepts"]) for r in all_results)
        total_mech_matches = sum(len(r["mechanical_matches"]) for r in all_results)

        f.write(f"Books processed:         {total_books}\n")
        f.write(f"  Successful:            {ok_books}\n")
        f.write(f"  Failed (no TOC):       {len(failures)}\n")
        f.write(f"Total headings found:    {total_headings}\n")
        f.write(f"LLM concepts extracted:  {total_llm_concepts}\n")
        f.write(f"Mechanical vocab matches:{total_mech_matches}\n")
        f.write(f"Final merged concepts:   {len(draft_mappings)}\n")
        f.write(f"New terms (gap report):  {len(new_terms)}\n\n")

        f.write("-" * 70 + "\n")
        f.write("PER-BOOK BREAKDOWN\n")
        f.write("-" * 70 + "\n\n")

        for r in all_results:
            status = "✅" if r["status"] == "ok" else "❌"
            f.write(f"{status} {r['filename']}\n")
            f.write(f"   Product: {r['product']}  |  TOC: {r['toc_method']}  |  "
                    f"Headings: {r['headings_count']}  |  "
                    f"LLM concepts: {len(r['concepts'])}  |  "
                    f"Vocab matches: {len(r['mechanical_matches'])}\n")

            if r["concepts"]:
                sample = list(r["concepts"].keys())[:8]
                f.write(f"   LLM samples: {', '.join(sample)}")
                if len(r["concepts"]) > 8:
                    f.write(f" ... +{len(r['concepts']) - 8} more")
                f.write("\n")
            f.write("\n")

    print(f"📝 Summary:       {summary_path}")


# ── CLI ────────────────────────────────────────────────────────────────────

def main():
    parser = argparse.ArgumentParser(
        description="Scour PDF guide TOCs and generate concept-to-guide mappings.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scour_books.py                           # All products, claude-sonnet-4
  python scour_books.py --product sdwan            # SD-WAN books only
  python scour_books.py --model gpt-4.1            # Use GPT-4.1
  python scour_books.py --book routing-book-xe.pdf # Single book
  python scour_books.py --dry-run                  # TOC extraction only, no LLM
        """,
    )
    parser.add_argument(
        "--product",
        choices=["sdwan", "ASR9000", "Cisco8000", "9800"],
        help="Process only this product folder",
    )
    parser.add_argument(
        "--book",
        help="Process only this specific PDF filename (must specify --product too)",
    )
    parser.add_argument(
        "--model",
        default="claude-sonnet-4",
        help="LLM model to use (default: claude-sonnet-4)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Extract TOCs only, skip LLM calls",
    )
    parser.add_argument(
        "--output-dir",
        type=Path,
        default=OUTPUT_DIR,
        help=f"Output directory (default: {OUTPUT_DIR})",
    )
    parser.add_argument(
        "--resume",
        action="store_true",
        help="Resume a previous run — skip books already in raw_results.json",
    )
    args = parser.parse_args()

    # ── Header ──
    print("=" * 70)
    print("📚 SCOUR BOOKS — TOC Extraction & Concept Mapping")
    print("=" * 70)

    # ── Load vocabulary ──
    print(f"\nLoading vocabulary from {TERMS_FILE.name}...")
    vocab = load_vocabulary()
    print(f"  {len(vocab)} terms loaded")

    # ── Load existing mappings ──
    print(f"Loading existing mappings from {MAPPINGS_FILE.name}...")
    existing = load_existing_mappings()
    print(f"  {len(existing)} existing concept entries")

    # ── Initialize LLM ──
    llm = None
    if not args.dry_run:
        print(f"\nInitializing LLM: {args.model}")
        try:
            load_dotenv()
            from utils import get_llm
            llm = get_llm(model_name=args.model, temperature=0)
            # Set request timeout so we don't hang forever on a slow API
            if hasattr(llm, "request_timeout"):
                llm.request_timeout = LLM_TIMEOUT
            if hasattr(llm, "timeout"):
                llm.timeout = LLM_TIMEOUT
            print(f"  ✅ LLM ready ({type(llm).__name__}, timeout={LLM_TIMEOUT}s)")
        except Exception as e:
            print(f"  ❌ LLM init failed: {e}")
            print("  Falling back to mechanical-only mode (like --dry-run)")
            args.dry_run = True

    # ── Discover books ──
    products = [args.product] if args.product else ["sdwan", "ASR9000", "Cisco8000", "9800"]
    all_books = []
    for prod in products:
        prod_dir = KNOWLEDGE_DIR / prod
        if not prod_dir.is_dir():
            print(f"\n⚠ Product folder not found: {prod_dir}")
            continue
        pdfs = sorted(prod_dir.glob("*.pdf"))
        if args.book:
            pdfs = [p for p in pdfs if p.name == args.book]
            if not pdfs:
                print(f"\n⚠ Book not found: {args.book} in {prod_dir}")
                continue
        for pdf in pdfs:
            all_books.append((pdf, prod))

    print(f"\n📁 Found {len(all_books)} PDF(s) to process across {len(products)} product(s)")

    if not all_books:
        print("Nothing to process. Exiting.")
        sys.exit(0)

    # ── Load previous results if resuming ──
    args.output_dir.mkdir(exist_ok=True)
    incremental_path = args.output_dir / "raw_results.json"
    completed_keys = set()   # "product/filename" keys already done
    all_results = []

    if args.resume and incremental_path.exists():
        try:
            with open(incremental_path) as f:
                all_results = json.load(f)
            for r in all_results:
                completed_keys.add(f"{r['product']}/{r['filename']}")
            print(f"  ♻️  Resuming — {len(completed_keys)} book(s) already done, skipping them")
        except Exception as e:
            print(f"  ⚠ Could not load previous results: {e}. Starting fresh.")
            all_results = []

    # ── Helper to (re)create LLM ──
    def create_llm():
        load_dotenv()
        # Delete cached token to force refresh
        cache_file = Path(__file__).parent / "auth_token_cache.json"
        if cache_file.exists():
            cache_file.unlink()
            print("  🔑 Cleared auth token cache")
        from utils import get_llm
        new_llm = get_llm(model_name=args.model, temperature=0)
        if hasattr(new_llm, "request_timeout"):
            new_llm.request_timeout = LLM_TIMEOUT
        if hasattr(new_llm, "timeout"):
            new_llm.timeout = LLM_TIMEOUT
        return new_llm

    # ── Process each book ──
    start_time = time.time()

    for i, (pdf_path, product) in enumerate(all_books, 1):
        book_key = f"{product}/{pdf_path.name}"

        if book_key in completed_keys:
            print(f"\n[{i}/{len(all_books)}] {book_key} — already done, skipping")
            continue

        print(f"\n{'─' * 60}")
        print(f"[{i}/{len(all_books)}] {book_key}")
        print(f"{'─' * 60}")

        result = process_book(pdf_path, product, llm, vocab, dry_run=args.dry_run)

        # Handle token expiration — refresh LLM and retry this book once
        if result == TOKEN_EXPIRED:
            print(f"\n  🔑 Refreshing LLM auth token...")
            try:
                llm = create_llm()
                print(f"  ✅ LLM refreshed, retrying {pdf_path.name}...")
                result = process_book(pdf_path, product, llm, vocab, dry_run=args.dry_run)
                if result == TOKEN_EXPIRED:
                    print(f"  ❌ Still failing after token refresh — skipping {pdf_path.name}")
                    continue
            except Exception as e:
                print(f"  ❌ LLM refresh failed: {e} — skipping {pdf_path.name}")
                continue

        all_results.append(result)

        # Incremental save after each book (crash-safe)
        serializable = []
        for r in all_results:
            sr = dict(r)
            sr["mechanical_matches"] = list(sr.get("mechanical_matches", {}).keys()) if isinstance(sr.get("mechanical_matches"), dict) else sr.get("mechanical_matches", [])
            serializable.append(sr)
        with open(incremental_path, "w") as f:
            json.dump(serializable, f, indent=2)

        # Small delay between LLM calls to be polite to the API
        if not args.dry_run and llm and result["status"] == "ok":
            time.sleep(1)

    elapsed = time.time() - start_time

    # ── Merge & output ──
    print(f"\n{'=' * 70}")
    print("MERGING RESULTS")
    print(f"{'=' * 70}")

    draft_mappings, new_terms, failures = merge_results(all_results, existing, vocab)

    save_outputs(draft_mappings, new_terms, failures, all_results, args.output_dir)

    # ── Final summary ──
    print(f"\n{'=' * 70}")
    print("DONE")
    print(f"{'=' * 70}")
    print(f"  Time:           {elapsed:.1f}s")
    print(f"  Books:          {len(all_results)} processed, {len(failures)} failed")
    print(f"  Concepts:       {len(draft_mappings)} total (merged)")
    print(f"  New terms:      {len(new_terms)} (not yet in vocabulary)")
    print(f"  Output:         {args.output_dir}/")

    if new_terms:
        print(f"\n💡 Review gap_report_new_terms.json — these concepts were found by the")
        print(f"   LLM but aren't in networking_terms.json yet. Add the useful ones!")

    if failures:
        print(f"\n⚠️  {len(failures)} book(s) had no extractable TOC. Consider manual review.")


if __name__ == "__main__":
    main()
