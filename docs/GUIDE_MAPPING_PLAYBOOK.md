# Guide-Mapping Playbook

---

## How to Use This Document (Instructions for You, the Human)

This playbook has two halves:

1. **Your steps** (this section) — what you do before, during, and after
2. **AI instructions** (everything below the line) — what you paste into the chat

### Before You Start
1. Gather all PDF documentation guides for the new product
2. Drop them into `knowledge_docs/<product_code>/` (create the folder if needed)
3. Run `scour_books.py` yourself in the terminal:
   ```bash
   # Dry run first to verify PDFs are readable:
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

Bug Doctor has a guide-scoring pipeline that narrows N documentation PDFs down to the top 3 most relevant guides for a given bug/RCA. It works like this:

1. `networking_terms.json` — a flat vocabulary (~1800 terms in 3 categories: protocols, technologies, features). The code scans RCA text against this vocabulary using word-boundary regex.
2. `guide_mappings.json` — maps each vocabulary term to one or more PDF guide filename patterns, **scoped per product**. The `concept_to_guide` key contains a sub-dict per product code (e.g. `"sdwan"`, `"ASR9000"`). When the code detects "bgp" in an RCA for product "sdwan", it looks up `concept_to_guide.sdwan.bgp → ["routing"]` and scores `routing-book-xe.pdf`. This per-product isolation ensures one product's mappings never contaminate another's rankings.
3. Scoring formula: `score = (inverse_breadth × freq_boost × specificity) ^ 0.7`
4. The top 3 scoring guides are auto-selected for the LLM agent to analyze.

There is also a script called `scour_books.py` that automates the heavy lifting:
- It reads each PDF's table of contents (bookmarks or text-scan)
- Sends headings to an LLM to extract concept-to-filename-pattern mappings
- Outputs `scour_output/draft_concept_mappings.json` (concepts already in the vocabulary)
- Outputs `scour_output/gap_report_new_terms.json` (concepts the LLM found but that are NOT in the vocabulary yet)
- Outputs `scour_output/raw_results.json` (full per-book details)

**Your role as the AI assistant is to help with everything scour_books.py does NOT do.** Scour handles Step 3 below. Everything else is human-judgment work that you help execute.

---

## The Workflow (Who Does What)

### Phase 1: Before the Scour (AI helps)

**Step 1 — I'll place the PDFs.** I will put all the product's documentation PDFs in `knowledge_docs/<product_code>/`. I'll tell you the product code (e.g. `ASR9000`, `Cisco8000`, `9800`).

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

**Step 5 — Merge scoured mappings.** Read `scour_output/draft_concept_mappings.json` and merge it into `guide_mappings.json` under `concept_to_guide.<product_code>` (e.g. `concept_to_guide.ASR9000`). Each product gets its own isolated sub-dict — **never merge into another product's section**. Rules:
- Create the product sub-key if it doesn't exist
- Keep existing manual entries at the top (before the `_comment_scoured` separator)
- Append scoured entries after the separator
- Union-merge: if a concept already exists *within the same product*, combine the pattern lists (deduplicated)
- All keys lowercase, all pattern values lowercase

**Step 6 — Identify reference/phone-book guides.** Read `scour_output/raw_results.json` and show me the LLM concept count per book (sorted descending). I'll tell you which ones are "phone books" — guides that match everything superficially (e.g. an alarms index). Add their filename patterns to `guide_mappings.json` under `reference_guides.patterns.<product_code>` (e.g. `reference_guides.patterns.ASR9000`). Each product has its own list of reference guide patterns. The scoring engine will exclude these from ranking; the UI will still show them unchecked with a "📋 Reference guide" label.

**Step 7 — Remove noise terms.** Help me find terms that match too many guides. Run the scoring against the full guide list and show me any term that maps to >60% of all guides. I'll tell you which ones to remove from `networking_terms.json`. Common culprits: the product name itself (e.g. `sdwan`, `ios xe`), generic words like `logs`.

**Step 8 — Install/upgrade triggers.** If this product has install or upgrade guides, check whether `guide_mappings.json` already has `install_upgrade_terms` entries that would match the new guide filenames. If not, add the new filename patterns to `install_upgrade_terms.guide_patterns`.

**Step 9 — Wire up the product.** Add the new product to:
- `product_mapping` dict in `app_functions.py` → `match_terms_to_guides()` (maps UI name to folder name)
- `product_noise` in `guide_mappings.json` (product-specific words to strip from filenames during matching, e.g. `{"ASR9000": ["asr", "9000", "9k"]}`)
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
1. Extracts TOC via PDF bookmarks (preferred) or text-scan of first 12 pages (fallback)
2. Sends headings to an LLM: "extract networking concepts and their synonyms, return JSON"
3. LLM returns: `{"bgp": ["routing"], "pim": ["routing", "multicast"], ...}`
4. Cross-references against `networking_terms.json` — in-vocab concepts go to `draft_concept_mappings.json`, out-of-vocab concepts go to `gap_report_new_terms.json`
5. Saves incrementally after each book (crash-safe with `--resume`)

SD-WAN run stats: 28 books, 4,124 headings, 2,248 LLM concepts, 1,810 final merged entries.

---

## Lessons Learned (Apply to Every Product)

1. **Per-product isolation is mandatory.** Each product's concept-to-guide mappings live under their own key in `concept_to_guide.<product_code>`. Terms like "acl" may map to `["policies","qos"]` for SD-WAN but `["ip","mpls","segment-routing"]` for ASR9000. Mixing them would break both products' scoring.

2. **Phone-book guides pollute rankings.** An alarms/reference guide with shallow coverage of every topic will score high on everything. Exclude it from scoring via `reference_guides.patterns.<product_code>` rather than trying to penalize it mathematically.

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
Number of PDF guides: _______________
PDFs are in: knowledge_docs/<code>/

I've already run scour_books.py and the outputs are in scour_output/.

Let's start with Phase 2 — reviewing the gap report and merging mappings.
```

--- END PASTE ---
