# Guide-Mapping Playbook

---

## How to Use This Document (Instructions for You, the Human)

This playbook has two halves:

1. **Your steps** (this section) — what you do before, during, and after
2. **AI instructions** (everything below the line) — what you paste into the chat

### Phase 0 — Documentation Pipeline (Preferred)

Before running scour, you need the raw documentation in `knowledge_docs/<product>/`. The recommended path is **HTML→Markdown** via the download pipeline. PDFs still work as a fallback.

#### Step 1: Create the Document Inventory

Create `inventory/<product>/document_inventory.json`. This is a JSON object keyed by book slug (e.g. `appqoe-book-xe.pdf`) with a `chapters` array:

```json
{
  "appqoe-book-xe.pdf": {
    "title": "Cisco Catalyst SD-WAN AppQoE Configuration Guide",
    "source_url": "https://www.cisco.com/c/en/us/td/docs/.../appqoe-book-xe.html",
    "chapters": [
      {
        "chapter_slug": "read-me-first",
        "chapter_title": "Read Me First",
        "chapter_url": "https://www.cisco.com/.../read-me-first.html"
      }
    ]
  }
}
```

Each book entry needs: a `title`, a `source_url` (the book's landing page), and a `chapters` array where each chapter has a `chapter_slug`, `chapter_title`, and `chapter_url` (direct link to the HTML page on cisco.com). This file is currently curated by hand — browse the product's documentation landing page to collect the URLs.

#### Step 2: Create a Download Script

Create `admin/download_<product>.py`. Use `admin/download_sdwan_html.py` as the template — it handles the full two-step pipeline:

| Step | Input | Output |
|------|-------|--------|
| 1. Download raw HTML | `chapter_url` from inventory | `data/html_archive/<product>/<book-slug>/<chapter>.html` |
| 2. Convert HTML → MD | cached `.html` file | `knowledge_docs/<product>/<book-slug>/<chapter>.md` |

Key features to carry over:
- **Skip logic**: If both `.html` and `.md` already exist, the chapter is skipped (unless `--force`)
- **Reconvert mode**: `--reconvert` re-runs HTML→Markdown from the cached `.html` files (no network)
- **Static book overrides**: For books whose ToC page is JS-rendered, add entries to `STATIC_BOOK_OVERRIDES` with a static ToC URL
- **markdownify conversion**: Strips nav/header/footer/script elements, extracts `#chapterContent` div, converts to Markdown

CLI usage examples (for SD-WAN):
```bash
python admin/download_sdwan_html.py                         # Download all, skip existing
python admin/download_sdwan_html.py --book appqoe-book-xe   # One book only
python admin/download_sdwan_html.py --force                  # Re-download everything
python admin/download_sdwan_html.py --reconvert              # Re-convert cached HTML only
python admin/download_sdwan_html.py --dry-run                # List books/chapters, no download
```

#### Step 3: Register in the Admin Page

To enable the download from the Streamlit Admin tab, add an entry to `PRODUCT_DOWNLOAD_REGISTRY` in `app/sidebar_admin_page.py`:

```python
"My Product (HTML Chapters)": {
    "module": "admin.download_<product>",
    "folder": os.path.join(KNOWLEDGE_DOCS_DIR, "<product>"),
    "supports_release_filter": False,
}
```

Then users can trigger the download from the Admin tab's **Download Documentation** section.

#### Step 4: Run the Download

Run the download script (CLI or Admin tab). Once complete, verify the Markdown files landed in `knowledge_docs/<product>/<book-slug>/`. Then proceed to "Before You Start" below to run scour and continue onboarding.

#### Step 5: Rebuild the Vector Store

After downloading, go to the Admin tab's **Vector Store** section and click **Rebuild Vector Store** (with the confirmation checkbox). This re-ingests everything in `knowledge_docs/` into ChromaDB. The rebuild is always a separate manual step — it does not happen automatically after download.

---

### Before You Start
1. Gather documentation guides for the new product. Preferred format is **Markdown** (HTML→Markdown via the Phase 0 pipeline above). PDFs are also supported as a fallback.
2. Drop them into `knowledge_docs/<product_code>/` (create the folder if needed). For Markdown guides, use the structure `knowledge_docs/<product>/<book-slug>/<chapter>.md`.
3. Run `scour_books.py` yourself in the terminal:
   ```bash
   # Dry run first to verify files are readable:
   python scour_books.py --dry-run --product <code>

   
   # Full scour (20-40 min, use --resume if it crashes):
   python scour_books.py --product <code>
   Example for human: python scour_books.py --product ASR9000
   
   ```
4. Wait for it to finish. Outputs land in `scour_output/`.

### Paste to the AI
1. Open a new chat with your AI coding assistant (GitHub Copilot, etc.)
2. Copy everything from **"--- START PASTE ---"** to **"--- END PASTE ---"** below
3. Paste it as your first message
4. Then send a follow-up message like:
   ```
   I'm onboarding [product name]. Product code is [code].
   I have [N] PDFs in knowledge_docs/[code]/.
   I already ran scour_books.py and outputs are in scour_output/.
   Let's start with Phase 2.
   ```
5. The AI will walk you through the rest — reviewing the gap report, merging mappings, identifying phone-book guides, removing noise, wiring up the product, and testing.

### During the Session
- The AI will ask you judgment calls: "Should I add this term?" "Is this a phone-book guide?" — answer yes/no.
- You provide the test RCAs (real bug content). The AI adds them to `debug_analysis.py` and runs scoring.
- If something looks wrong in the rankings, tell the AI what you expected and it'll help diagnose.

### After You're Done
- Run the app (`streamlit run sidebar_app.py`) and test with a real bug
- Commit everything to git

---
--- START PASTE ---

# Guide-Mapping Playbook — Instructions for AI Assistant

> **What this is:** Instructions for onboarding a new product set into Bug Doctor's guide-scoring engine. You (the AI) handle all file editing; `scour_books.py` has already been run; the human makes judgment calls.

---

## Context for the AI

Bug Doctor has a guide-scoring pipeline that narrows N documentation guides down to the top 3 most relevant for a given bug/RCA. It works like this:

1. `networking_terms.json` — a flat vocabulary (~1800 terms in 3 categories: protocols, technologies, features). The code scans RCA text against this vocabulary using word-boundary regex.
2. `ontology/<product>/guide_mappings.json` — maps each vocabulary term to one or more guide filename patterns, **scoped per product**. When the code detects "bgp" in an RCA for product "sdwan", it looks up `concept_to_guide.bgp → ["routing"]` and scores `routing-book-xe`. This per-product isolation ensures one product's mappings never contaminate another's. Shared cross-product settings (stop words, noise words) live in `ontology/_shared/guide_mappings.json`.
3. Scoring formula: `score = (inverse_breadth × freq_boost × specificity) ^ 0.7`
4. The top 3 scoring guides are auto-selected for the LLM agent to analyze.

There is also a script called `scour_books.py` that automates the heavy lifting:
- It reads each guide's table of contents (PDF bookmarks, text-scan, or Markdown headings)
- Sends headings to an LLM to extract concept-to-filename-pattern mappings
- Outputs `scour_output/draft_concept_mappings.json` (concepts already in the vocabulary)
- Outputs `scour_output/gap_report_new_terms.json` (concepts the LLM found but that are NOT in the vocabulary yet)
- Outputs `scour_output/raw_results.json` (full per-book details)

**Your role as the AI assistant is to help with everything scour_books.py does NOT do.** Scour handles Step 3 below. Everything else is human-judgment work that you help execute.

---

## The Workflow (Who Does What)

### Phase 1: Before the Scour (AI helps)

**Step 1 — I'll place the documentation.** I will put all the product's documentation guides in `knowledge_docs/<product_code>/`. For Markdown guides the structure is `knowledge_docs/<product>/<book-slug>/<chapter>.md`. I'll tell you the product code (e.g. `ASR9000`, `Cisco8000`, `9800`).

**Step 2 — Seed product-specific vocabulary.** Read the existing `networking_terms.json`. Most protocol/technology terms already exist. I'll give you a list of product-specific feature phrases to add (or you suggest them based on the product). Add them to the `features` array. Rules:
- All lowercase
- Multi-word terms are more valuable (2× scoring bonus) — prefer "route policy" over "policy"
- Include both acronym and expanded form
- Think "what would an engineer type in a bug report"

**Step 3 — I run `scour_books.py`.** This is my step. I'll run it in the terminal:
```bash
python scour_books.py --product <code>
```
It takes 20-40 minutes. Uses `--resume` if it crashes. When it finishes, I'll tell you.

### Phase 2: After the Scour (AI helps)

**Step 4 — Review the gap report.** Read `scour_output/gap_report_new_terms.json`. For each term, I'll tell you whether to add it to the vocabulary or skip it. You add the ones I approve to `networking_terms.json`.

**Step 5 — Merge scoured mappings.** Read `scour_output/draft_concept_mappings.json` and merge it into `ontology/<product_code>/guide_mappings.json` under `concept_to_guide`. Each product has its own file — **never merge into another product's file**. Rules:
- Create the product file/folder if it doesn't exist (`ontology/<product_code>/guide_mappings.json`)
- Keep existing manual entries at the top (before the `_comment_scoured` separator)
- Append scoured entries after the separator
- Union-merge: if a concept already exists, combine the pattern lists (deduplicated)
- All keys lowercase, all pattern values lowercase

**Step 6 — Identify reference/phone-book guides.** Read `scour_output/raw_results.json` and show me the LLM concept count per book (sorted descending). I'll tell you which ones are "phone books" — guides that match everything superficially (e.g. an alarms index). Add their filename patterns to `ontology/<product_code>/guide_mappings.json` under `reference_guides.patterns`. The scoring engine will exclude these from ranking; the UI will still show them unchecked with a "📋 Reference guide" label.

**Step 7 — Remove noise terms.** Help me find terms that match too many guides. Run the scoring against the full guide list and show me any term that maps to >60% of all guides. I'll tell you which ones to remove from `networking_terms.json`. Common culprits: the product name itself (e.g. `sdwan`, `ios xe`), generic words like `logs`.

**Step 8 — Install/upgrade triggers.** If this product has install or upgrade guides, check whether `ontology/_shared/guide_mappings.json` already has `install_upgrade_terms` entries that would match the new guide filenames. If not, add the new filename patterns to `install_upgrade_terms.guide_patterns`.

**Step 9 — Wire up the product.** Add the new product to:
- `product_mapping` dict in `app_functions.py` → `match_terms_to_guides()` (maps UI name to folder name)
- `product_noise` in `ontology/<product_code>/guide_mappings.json` (product-specific words to strip from filenames during matching, e.g. `["asr", "9000", "9k"]`)
- The sidebar product dropdown in `sidebar_app.py` if it's not already there

### Phase 3: Test & Tune (AI helps)

**Step 10 — Test with real RCAs.** I'll give you 3-5 real bug/RCA texts and tell you which guide should win for each. Add them as test cases in `debug_analysis.py` and run `python debug_analysis.py --rca <name> --no-llm` to check the scoring. Show me the ranked results.

**What to look for:**
- Does the correct guide land in the top 3?
- Are "catch-all" guides dominating unfairly? (symptom: one guide wins everything)
- Is the gap between #3 and #4 meaningful? (< 0.5 points = fragile)

**Step 11 — Tune scoring (if needed).** The constants are in `app_functions.py` → `match_terms_to_guides()`:
| Constant | Current | Purpose |
|----------|---------|---------|
| `FREQ_BOOST_CAP` | 3.0 | Caps frequency multiplier (`log2(count)+1`) |
| `MULTIWORD_BONUS` | 2.0 | Multi-word terms get this multiplier |
| `DIMINISHING_EXPONENT` | 0.7 | Compresses high scores (< 1.0 = compression) |

Only change these if test RCAs reveal systemic issues, not for one-off edge cases.

---

## What scour_books.py Does (For Reference)

You do NOT need to replicate any of this. It already exists and I will run it.

Per book:
1. Extracts TOC via PDF bookmarks, text-scan of first 12 pages, or Markdown headings
2. Sends headings to an LLM: "extract networking concepts and their synonyms, return JSON"
3. LLM returns: `{"bgp": ["routing"], "pim": ["routing", "multicast"], ...}`
4. Cross-references against `networking_terms.json` — in-vocab concepts go to `draft_concept_mappings.json`, out-of-vocab concepts go to `gap_report_new_terms.json`
5. Saves incrementally after each book (crash-safe with `--resume`)

SD-WAN run stats: 28 books, 4,124 headings, 2,248 LLM concepts, 1,810 final merged entries.

---

## Lessons Learned (Apply to Every Product)

1. **Per-product isolation is mandatory.** Each product's concept-to-guide mappings live in their own file at `ontology/<product_code>/guide_mappings.json`. Terms like "acl" may map to `["policies","qos"]` for SD-WAN but `["ip","mpls","segment-routing"]` for ASR9000. Mixing them would break both products' scoring.

2. **Phone-book guides pollute rankings.** An alarms/reference guide with shallow coverage of every topic will score high on everything. Exclude it from scoring via `reference_guides.patterns` in the product's ontology file rather than trying to penalize it mathematically.

2. **Product-name terms are poison.** If a term appears in every guide's filename for that product, it matches all guides equally → zero signal. Remove it from the vocabulary.

3. **Multi-word terms are gold.** "dns security" is far more informative than "dns". The 2× specificity bonus reflects this.

4. **Frequency matters.** A term mentioned 8× in an RCA is more relevant than one mentioned once. The `log2(freq)+1` boost (capped at 3.0) handles this.

5. **The gap report is the fastest way to expand coverage.** After scouring, the gap report shows what the LLM found important but the vocabulary doesn't know yet.

6. **The LLM can override the code — and that's OK.** The scoring engine does best-effort mechanical ranking. The LLM agent has reading comprehension and may pick a different guide. That's fine. The code's job is to give the LLM a good starting set.

---

## Quick-Start Template

When you paste this to start a new product, fill in the blanks:

```
I'm onboarding a new product into Bug Doctor. Here's what I have:

Product name: _______________
Product code (folder name): _______________
Number of documentation guides: _______________
Guides are in: knowledge_docs/<code>/

I've already run scour_books.py and the outputs are in scour_output/.

Let's start with Phase 2 — reviewing the gap report and merging mappings.
```

--- END PASTE ---
