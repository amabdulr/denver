#!/usr/bin/env python3
"""
build_taxonomy.py — Build a static, writer-reviewable taxonomy of every
book → chapter → section in the documentation library, tagged with concepts.

The output lives in  taxonomy/<product>/taxonomy.json  and is:
  • Static — generated once, reviewed by writers, treated as ground truth.
  • Hierarchical — preserves the Book → Chapter → Section nesting from PDF bookmarks.
  • Concept-tagged — each node carries a list of networking concepts extracted
    mechanically from networking_terms.json AND (optionally) enriched by an LLM.
  • URL-enriched — chapter URLs are pulled from document_inventory.json when available.

Workflow:
  1. Extract hierarchical bookmarks from each PDF (depth preserved).
  2. Fall back to text-scan TOC if bookmarks are missing.
  3. Merge chapter-level URLs from document_inventory.json.
  4. Tag every node with concepts from networking_terms.json (mechanical).
  5. (Optional) Send each chapter's sub-headings to an LLM for deeper concept extraction.
  6. Write taxonomy/<product>/taxonomy.json.

The generated file is meant to be committed alongside knowledge_docs/ and
reviewed by writers — just like the PDFs themselves.  The app can later
consume it as a static lookup instead of computing guide/chapter matches
at runtime.

Usage:
  python scripts/build_taxonomy.py                             # All products
  python scripts/build_taxonomy.py --product sdwan             # One product
  python scripts/build_taxonomy.py --product sdwan --dry-run   # No LLM, mechanical only
  python scripts/build_taxonomy.py --product sdwan --book routing-book-xe.pdf
  python scripts/build_taxonomy.py --model gpt-4.1             # Different model
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

# ── Paths (relative to project root, not scripts/) ────────────────────────

PROJECT_ROOT = Path(__file__).resolve().parent.parent
KNOWLEDGE_DIR = PROJECT_ROOT / "knowledge_docs"
CONFIG_DIR = PROJECT_ROOT / "config"
INVENTORY_DIR = PROJECT_ROOT / "inventory"
TAXONOMY_DIR = PROJECT_ROOT / "taxonomy"
TERMS_FILE = CONFIG_DIR / "networking_terms.json"

# Max headings to send in a single LLM call
CHUNK_SIZE = 80
MAX_RETRIES = 3
LLM_TIMEOUT = 180


# ══════════════════════════════════════════════════════════════════════════
#  TOC Extraction  —  Hierarchical
# ══════════════════════════════════════════════════════════════════════════

def extract_bookmarks_hierarchical(pdf_path: Path, max_depth: int = 4) -> list[dict]:
    """
    Extract bookmark/outline headings from a PDF, preserving hierarchy.

    Returns a nested list of dicts:
        [
            {"title": "Chapter 1: BGP", "level": 0, "children": [
                {"title": "Configure eBGP", "level": 1, "children": [...]},
            ]},
        ]
    Also returns a flat ordered list for fallback matching.
    """
    from pypdf import PdfReader

    try:
        reader = PdfReader(str(pdf_path))
        outline = reader.outline
        if not outline:
            return []
    except Exception:
        return []

    flat: list[dict] = []

    def walk(items, depth=0):
        if depth >= max_depth:
            return
        for item in items:
            if isinstance(item, list):
                walk(item, depth + 1)
            elif hasattr(item, "title"):
                title = item.title.strip()
                if title:
                    flat.append({"title": title, "level": depth})

    walk(outline)
    return flat


def extract_toc_from_text(pdf_path: Path, max_pages: int = 12) -> list[dict]:
    """
    Fallback: scan first N pages for TOC-style lines.
    All entries get level=1 (we can't infer hierarchy from plain text reliably).
    """
    from pypdf import PdfReader

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
    toc_patterns = [
        re.compile(r"(?:chapter|part|section)\s*\d+[:\.\s]+(.+?)(?:\s*\.{2,}\s*\d+|\s+\d+\s*$)", re.IGNORECASE),
        re.compile(r"^(.{10,80}?)\s*\.{3,}\s*\d+", re.MULTILINE),
        re.compile(r"^(.{10,80}?)\s{3,}\d{1,4}\s*$", re.MULTILINE),
    ]

    seen = set()
    for pattern in toc_patterns:
        for match in pattern.finditer(raw_text):
            heading = match.group(1).strip()
            if len(heading) < 5 or len(heading) > 120:
                continue
            if heading.lower().startswith(("page", "table", "figure", "©", "cisco")):
                continue
            key = heading.lower().strip()
            if key not in seen:
                seen.add(key)
                headings.append({"title": heading, "level": 1})

    return headings


def extract_toc(pdf_path: Path) -> tuple[list[dict], str]:
    """Try hierarchical bookmarks first, fall back to text scan."""
    entries = extract_bookmarks_hierarchical(pdf_path)
    if entries:
        return entries, "bookmarks"

    entries = extract_toc_from_text(pdf_path)
    if entries:
        return entries, "text_scan"

    return [], "none"


# ══════════════════════════════════════════════════════════════════════════
#  Nest flat entries into a tree
# ══════════════════════════════════════════════════════════════════════════

def _build_tree(flat_entries: list[dict]) -> list[dict]:
    """
    Convert a flat list of {"title", "level"} dicts into a nested tree
    where each node has a "sections" list of children.

    Strategy: use a stack. When we see a deeper level, push onto the
    current node's sections. When we see the same or shallower level,
    pop back up.
    """
    root: list[dict] = []
    stack: list[tuple[int, list]] = [(-1, root)]  # (level, children list)

    for entry in flat_entries:
        node = {
            "title": entry["title"],
            "level": entry["level"],
            "concepts": [],  # filled later
            "sections": [],
        }

        # Pop up until we find a parent whose level is strictly less
        while stack and stack[-1][0] >= entry["level"]:
            stack.pop()

        if not stack:
            stack = [(-1, root)]

        # Append to current parent's children
        parent_children = stack[-1][1]
        parent_children.append(node)

        # Push this node so deeper entries nest inside it
        stack.append((entry["level"], node["sections"]))

    return root


# ══════════════════════════════════════════════════════════════════════════
#  Vocabulary / Networking Terms
# ══════════════════════════════════════════════════════════════════════════

def load_vocabulary() -> set[str]:
    """Load all terms from networking_terms.json into a flat set (lowercase)."""
    with open(TERMS_FILE, encoding="utf-8") as f:
        data = json.load(f)

    terms = set()
    for key, value in data.items():
        if key.startswith("_"):
            continue
        if isinstance(value, list):
            for t in value:
                terms.add(t.lower().strip())
    return terms


_SKIP_HEADINGS = {
    "contents", "preface", "audience", "documentation conventions",
    "communications, services, and additional information",
    "related documentation", "obtaining documentation and submitting a service request",
    "document change history", "changes to this document",
    "new and changed information", "what's new", "read me first",
    "introduction", "overview", "glossary", "index", "appendix",
    "feature history", "feature information", "references",
    "prerequisites", "restrictions", "guidelines and limitations",
}


def tag_node_concepts(node: dict, vocab: set[str]):
    """
    Recursively tag a tree node (and all descendants) with matching
    networking terms from vocab.  Tags are attached to the most specific
    (deepest) node where they appear.
    """
    title_lower = node["title"].lower()

    # Skip boilerplate headings
    if title_lower.strip() in _SKIP_HEADINGS:
        node["concepts"] = []
    else:
        matched = []
        for term in vocab:
            pattern = r"\b" + re.escape(term) + r"\b"
            if re.search(pattern, title_lower):
                matched.append(term)
        # Sort: longer (more specific) terms first
        matched.sort(key=lambda t: (-len(t), t))
        node["concepts"] = matched

    for child in node.get("sections", []):
        tag_node_concepts(child, vocab)


# ══════════════════════════════════════════════════════════════════════════
#  LLM Concept Enrichment (per-chapter)
# ══════════════════════════════════════════════════════════════════════════

LLM_PROMPT = """\
You are a Cisco networking documentation expert.  I am building a \
taxonomy that maps documentation chapters/sections to networking concepts.

Below are the HEADINGS from one chapter (and its sub-sections) of a Cisco \
documentation guide.

**Book:** {book_title}
**Product:** {product}
**Chapter:** {chapter_title}

**Sub-headings in this chapter:**
{headings}

Your task:
1. For the chapter AND each sub-heading, list the **networking concepts** \
   a Cisco engineer would use when describing a bug related to that topic.
2. Include abbreviations, synonyms, and related sub-protocols.
3. Only return concepts relevant to the chapter — not generic terms.

**Output format:** Return a JSON object where keys are the EXACT heading \
strings from the input, and values are arrays of lowercase concept strings.

Example:
```json
{{
  "Configure OSPF Routing": ["ospf", "routing", "area border router", "lsa", "spf"],
  "OSPF Route Redistribution": ["route redistribution", "ospf", "redistribute"]
}}
```

Return ONLY the JSON object, no other text.
"""


def _try_parse_json(content: str) -> Optional[dict]:
    """Parse JSON with fallback repair for truncated responses."""
    if content.startswith("```"):
        content = re.sub(r"^```(?:json)?\s*", "", content)
        content = re.sub(r"\s*```\s*$", "", content)
    try:
        return json.loads(content)
    except json.JSONDecodeError:
        pass
    last_bracket = content.rfind("]")
    if last_bracket > 0:
        repaired = content[:last_bracket + 1].rstrip().rstrip(",") + "\n}"
        try:
            return json.loads(repaired)
        except json.JSONDecodeError:
            pass
    return None


def enrich_chapter_with_llm(
    chapter_node: dict,
    book_title: str,
    product: str,
    llm,
) -> None:
    """
    Send a chapter's sub-headings to the LLM and merge returned concepts
    into the tree nodes (additive — does not overwrite mechanical tags).
    """
    # Collect all headings in this chapter subtree
    def collect_titles(node):
        titles = [node["title"]]
        for child in node.get("sections", []):
            titles.extend(collect_titles(child))
        return titles

    all_titles = collect_titles(chapter_node)
    if len(all_titles) <= 1:
        return  # Nothing interesting for the LLM

    headings_text = "\n".join(f"  - {t}" for t in all_titles)

    prompt = LLM_PROMPT.format(
        book_title=book_title,
        product=product,
        chapter_title=chapter_node["title"],
        headings=headings_text,
    )

    for attempt in range(1, MAX_RETRIES + 1):
        try:
            response = llm.invoke(prompt)
            content = response.content.strip()
            result = _try_parse_json(content)
            if result is None:
                if attempt < MAX_RETRIES:
                    time.sleep(5)
                    continue
                return
            break
        except Exception as e:
            err_str = str(e)
            if "401" in err_str or "token" in err_str.lower():
                print(f"      🔑 Token expired — caller should refresh")
                return  # Let caller handle
            if attempt < MAX_RETRIES:
                time.sleep(10)
                continue
            return
    else:
        return

    # Merge LLM concepts into the tree
    def merge_into(node):
        llm_concepts = result.get(node["title"], [])
        if isinstance(llm_concepts, list):
            existing = set(node.get("concepts", []))
            for c in llm_concepts:
                c_clean = str(c).lower().strip()
                if c_clean and c_clean not in existing:
                    existing.add(c_clean)
            node["concepts"] = sorted(existing)
        for child in node.get("sections", []):
            merge_into(child)

    merge_into(chapter_node)


# ══════════════════════════════════════════════════════════════════════════
#  Document Inventory Merging (URLs)
# ══════════════════════════════════════════════════════════════════════════

def load_document_inventory(product: str) -> dict:
    """Load document_inventory.json for a product, if it exists."""
    inv_path = INVENTORY_DIR / product / "document_inventory.json"
    if inv_path.is_file():
        try:
            with open(inv_path, encoding="utf-8") as f:
                return json.load(f)
        except Exception as e:
            print(f"    ⚠ Could not load {inv_path}: {e}")
    return {}


def attach_urls(book_node: dict, inventory_entry: dict):
    """
    Walk the book tree and attach chapter_url + chapter_slug from the
    inventory to matching chapter nodes (level-1 children of the book).
    Matching is by normalized title comparison.
    """
    chapters_inv = inventory_entry.get("chapters", [])
    if not chapters_inv:
        return

    # Build a lookup: normalized title → inventory chapter dict
    inv_lookup = {}
    for ch in chapters_inv:
        key = ch.get("chapter_title", "").lower().strip()
        if key:
            inv_lookup[key] = ch

    # Walk top-level sections (= chapters)
    for section in book_node.get("chapters", []):
        key = section["title"].lower().strip()
        inv_match = inv_lookup.get(key)
        if inv_match:
            section["chapter_url"] = inv_match.get("chapter_url", "")
            section["chapter_slug"] = inv_match.get("chapter_slug", "")


# ══════════════════════════════════════════════════════════════════════════
#  Cleanup — remove empty concept lists and prune noise
# ══════════════════════════════════════════════════════════════════════════

def _cleanup_node(node: dict):
    """Remove empty concepts arrays and prune level field for cleanliness."""
    # Remove the 'level' key — it was only needed during tree building
    node.pop("level", None)

    if not node.get("concepts"):
        node.pop("concepts", None)

    # Rename 'sections' → keep as-is (it's the hierarchy key)
    for child in node.get("sections", []):
        _cleanup_node(child)

    # Remove empty sections list
    if not node.get("sections"):
        node.pop("sections", None)


# ══════════════════════════════════════════════════════════════════════════
#  Process One Book
# ══════════════════════════════════════════════════════════════════════════

def process_book(
    pdf_path: Path,
    product: str,
    vocab: set[str],
    inventory: dict,
    llm=None,
    dry_run: bool = False,
) -> Optional[dict]:
    """
    Process a single PDF and return a taxonomy book node:
    {
      "filename": "routing-book-xe.pdf",
      "title": "Cisco Catalyst SD-WAN Routing Configuration Guide...",
      "source_url": "https://...",
      "toc_method": "bookmarks",
      "chapters": [
        {
          "title": "Configure BGP Routing",
          "chapter_url": "...",
          "chapter_slug": "...",
          "concepts": ["bgp", "autonomous system"],
          "sections": [
            {"title": "eBGP Configuration", "concepts": ["ebgp"]},
          ]
        }
      ]
    }
    """
    filename = pdf_path.name
    print(f"\n  📖 {filename}")

    # Step 1: Extract TOC
    flat_entries, method = extract_toc(pdf_path)
    print(f"     TOC method: {method}, entries: {len(flat_entries)}")

    if not flat_entries:
        print(f"     ⚠ No TOC extracted — skipping")
        return None

    # Show first few
    for e in flat_entries[:5]:
        indent = "  " * e["level"]
        print(f"       {indent}• {e['title'][:70]}")
    if len(flat_entries) > 5:
        print(f"       ... and {len(flat_entries) - 5} more")

    # Step 2: Build tree
    tree = _build_tree(flat_entries)

    # Step 3: Tag concepts mechanically
    for node in tree:
        tag_node_concepts(node, vocab)

    # Step 4: Enrich with LLM (per chapter, not whole book)
    if not dry_run and llm:
        # Top-level nodes are "chapters"
        for i, chapter_node in enumerate(tree):
            # Skip boilerplate chapters
            if chapter_node["title"].lower().strip() in _SKIP_HEADINGS:
                continue
            print(f"     🤖 LLM enriching chapter {i+1}/{len(tree)}: {chapter_node['title'][:60]}...")
            enrich_chapter_with_llm(chapter_node, filename, product, llm)
            time.sleep(0.5)  # rate limit

    # Step 5: Attach inventory URLs
    inv_entry = inventory.get(filename, {})
    book_title = inv_entry.get("title", filename.replace(".pdf", "").replace("-", " ").title())
    source_url = inv_entry.get("source_url", "")

    book_node = {
        "filename": filename,
        "title": book_title,
        "source_url": source_url,
        "toc_method": method,
        "chapters": tree,
    }

    attach_urls(book_node, inv_entry)

    # Cleanup
    for ch in book_node["chapters"]:
        _cleanup_node(ch)

    chapter_count = len(book_node["chapters"])
    concept_count = _count_concepts(book_node)
    print(f"     ✅ {chapter_count} chapters, {concept_count} concept tags")

    return book_node


def _count_concepts(node: dict) -> int:
    """Count total concept tags across the whole tree."""
    count = len(node.get("concepts", []))
    for child in node.get("chapters", node.get("sections", [])):
        count += _count_concepts(child)
    return count


# ══════════════════════════════════════════════════════════════════════════
#  Main
# ══════════════════════════════════════════════════════════════════════════

def main():
    parser = argparse.ArgumentParser(
        description="Build a static, writer-reviewable documentation taxonomy.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python scripts/build_taxonomy.py                              # All products
  python scripts/build_taxonomy.py --product sdwan              # SD-WAN only
  python scripts/build_taxonomy.py --product sdwan --dry-run    # No LLM
  python scripts/build_taxonomy.py --product ASR9000 --book b-routing-cg-asr9000-25xx.pdf
  python scripts/build_taxonomy.py --model gpt-4.1              # Different model
        """,
    )
    parser.add_argument(
        "--product",
        choices=["sdwan", "ASR9000", "Cisco8000", "9800", "cisco_generic"],
        help="Process only this product folder",
    )
    parser.add_argument(
        "--book",
        help="Process only this specific PDF filename (must also specify --product)",
    )
    parser.add_argument(
        "--model",
        default="gpt-4.1",
        help="LLM model for concept enrichment (default: gpt-4.1)",
    )
    parser.add_argument(
        "--dry-run",
        action="store_true",
        help="Mechanical concept tagging only — skip LLM calls",
    )

    args = parser.parse_args()

    print("=" * 70)
    print("🌳 BUILD TAXONOMY — Static Documentation Map")
    print("=" * 70)

    # ── Load vocabulary ──
    print(f"\n📖 Loading vocabulary from {TERMS_FILE.name}...")
    vocab = load_vocabulary()
    print(f"   {len(vocab)} terms loaded")

    # ── Initialize LLM ──
    llm = None
    if not args.dry_run:
        print(f"\n🤖 Initializing LLM: {args.model}")
        try:
            load_dotenv(PROJECT_ROOT / ".env")
            # Add app/ to path so we can import utils
            sys.path.insert(0, str(PROJECT_ROOT / "app"))
            from utils import get_llm
            llm = get_llm(model_name=args.model, temperature=0)
            if hasattr(llm, "request_timeout"):
                llm.request_timeout = LLM_TIMEOUT
            if hasattr(llm, "timeout"):
                llm.timeout = LLM_TIMEOUT
            print(f"   ✅ LLM ready")
        except Exception as e:
            print(f"   ❌ LLM init failed: {e}")
            print(f"   Falling back to mechanical-only mode (like --dry-run)")
            args.dry_run = True

    # ── Discover products and books ──
    products = [args.product] if args.product else ["sdwan", "ASR9000", "Cisco8000", "9800"]
    total_books = 0
    total_chapters = 0
    total_concepts = 0

    for product in products:
        prod_dir = KNOWLEDGE_DIR / product
        if not prod_dir.is_dir():
            print(f"\n⚠ Product folder not found: {prod_dir}")
            continue

        pdfs = sorted(prod_dir.glob("*.pdf"))
        if args.book:
            pdfs = [p for p in pdfs if p.name == args.book]
            if not pdfs:
                print(f"\n⚠ Book not found: {args.book} in {prod_dir}")
                continue

        print(f"\n{'━' * 70}")
        print(f"📁 Product: {product}  ({len(pdfs)} PDF{'s' if len(pdfs) != 1 else ''})")
        print(f"{'━' * 70}")

        # Load inventory for this product
        inventory = load_document_inventory(product)
        if inventory:
            print(f"   📋 Document inventory loaded ({len(inventory)} guides with URLs)")
        else:
            print(f"   ℹ️  No document inventory found (URLs will be empty)")

        # Process each book
        taxonomy_books: list[dict] = []

        for i, pdf_path in enumerate(pdfs, 1):
            print(f"\n  [{i}/{len(pdfs)}]", end="")
            book_node = process_book(
                pdf_path, product, vocab, inventory,
                llm=llm, dry_run=args.dry_run,
            )
            if book_node:
                taxonomy_books.append(book_node)
                total_books += 1
                total_chapters += len(book_node.get("chapters", []))
                total_concepts += _count_concepts(book_node)

            # Rate limiting between books
            if not args.dry_run and llm:
                time.sleep(1)

        # ── Write output ──
        if taxonomy_books:
            out_dir = TAXONOMY_DIR / product
            out_dir.mkdir(parents=True, exist_ok=True)
            out_path = out_dir / "taxonomy.json"

            taxonomy_doc = {
                "_comment": (
                    "Auto-generated documentation taxonomy. "
                    "Writers: review and edit concept tags, then commit. "
                    "Generated by: python scripts/build_taxonomy.py"
                ),
                "_product": product,
                "_book_count": len(taxonomy_books),
                "books": taxonomy_books,
            }

            with open(out_path, "w", encoding="utf-8") as f:
                json.dump(taxonomy_doc, f, indent=2, ensure_ascii=False)

            print(f"\n  ✅ Written: {out_path}")
            print(f"     {len(taxonomy_books)} books, "
                  f"{sum(len(b.get('chapters', [])) for b in taxonomy_books)} chapters")
        else:
            print(f"\n  ⚠ No books processed for {product}")

    # ── Summary ──
    print(f"\n{'=' * 70}")
    print("🏁 TAXONOMY BUILD COMPLETE")
    print(f"{'=' * 70}")
    print(f"   Books:    {total_books}")
    print(f"   Chapters: {total_chapters}")
    print(f"   Concepts: {total_concepts} tags total")
    print(f"   Output:   {TAXONOMY_DIR}/")
    print()
    print("📝 Next steps:")
    print("   1. Review taxonomy/<product>/taxonomy.json")
    print("   2. Edit concept tags — add missing terms, remove noise")
    print("   3. Commit the file alongside your knowledge_docs/")
    print("   4. The app will consume it as a static lookup")


if __name__ == "__main__":
    main()
