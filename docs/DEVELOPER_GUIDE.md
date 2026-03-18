# 🩺 Denver App — Developer Guide

> **Bug Doctor: Cisco Documentation Assistant**
> An AI-powered Streamlit application that helps technical writers analyze bugs, locate relevant documentation, generate first drafts, and resolve CDETS bugs — all backed by a RAG (Retrieval-Augmented Generation) pipeline over Cisco product PDF guides.

---

## Table of Contents

1. [Architecture Overview](#architecture-overview)
2. [Project Folder Reference](#project-folder-reference)
3. [Application Entry Points](#application-entry-points)
4. [The Six App Pages](#the-six-app-pages)
5. [JSON Files — The Complete Reference](#json-files--the-complete-reference)
6. [Concept-to-Topic Mapping: How It Works](#concept-to-topic-mapping-how-it-works)
7. [Adding a New Product — Step-by-Step](#adding-a-new-product--step-by-step)
8. [Taxonomy — Static Documentation Map](#taxonomy--static-documentation-map)
9. [Prompt Templates](#prompt-templates)
10. [DITA XML Templates](#dita-xml-templates)
11. [Scripts & Utilities](#scripts--utilities)
12. [Knowledge Docs Pipeline — HTML & Markdown Conversion](#knowledge-docs-pipeline--html--markdown-conversion)
13. [Testing RCA Analysis Without Streamlit](#testing-rca-analysis-without-streamlit)
14. [Docker Deployment](#docker-deployment)

---

## Architecture Overview

```
┌────────────────────────────────────────────────────────────────┐
│                      User (Browser)                            │
│                  Streamlit Web Interface                        │
└─────────────────────────┬──────────────────────────────────────┘
                          │
          ┌───────────────▼───────────────────┐
          │   app/sidebar_app.py              │ ← Main UI controller
          │   (Page Router + Session State)    │
          └──┬────┬────┬────┬────┬───────────┘
             │    │    │    │    │
   ┌─────┐ ┌┴─┐ ┌┴──┐ ┌┴─┐ ┌┴──┐
   │Analy│ │FD│ │Blk│ │Res│ │Hal│  ← 5 sidebar pages
   │sis  │ │  │ │   │ │  │ │   │
   └──┬──┘ └┬─┘ └┬──┘ └┬─┘ └┬──┘
      │      │    │     │    │
      └──────┴────┴─────┴────┘
                  │
     ┌────────────▼──────────────┐
     │    app/app_functions.py   │ ← "Engine Room" — all business logic
     │  (RAG search, agents,     │
     │   term matching, scoring) │
     └────────────┬──────────────┘
                  │
     ┌────────────▼──────────────┐
     │ app/vector_store_manager  │ ← ChromaDB singleton (persistent or in-memory)
     │ app/ingestion.py          │ ← PDF/MD → Document chunking pipeline
     │ app/utils.py              │ ← LLM provider abstraction (CX-AI / BridgeIt)
     │ app/bug2.py               │ ← CDETS API client (OAuth1)
     └────────────┬──────────────┘
                  │
     ┌────────────▼──────────────┐
     │  config/*.json            │ ← All configuration (no code changes needed)
     │  ontology/<product>        │ ← Per-product guide mappings & knowledge graph
     │  prompts/*.md             │ ← All LLM prompt templates
     │  knowledge_docs/<product> │ ← PDF guides per product (vector store source)
     │  inventory/<product>      │ ← Document inventories with chapter URLs
     │  data/                    │ ← Runtime caches and auth tokens
     └──────────────────────────┘
```

### Key Design Principles

| Principle | Implementation |
|---|---|
| **Configuration over code** | Product keywords, guide mappings, networking terms — all in JSON files under `config/` and `ontology/`. No Python changes needed for most customizations. |
| **Prompt-as-file** | Every LLM prompt lives in `prompts/*.md`. Edit the markdown to change AI behavior without touching code. |
| **Product-agnostic** | The same app serves SD-WAN, 9800, ASR 9000, Cisco 8000, and `cisco_generic`. Adding a product is a data task, not a code task. |
| **Singleton vector store** | `vector_store_manager.py` holds one global ChromaDB instance. Auto-detects SQLite version and falls back to in-memory if < 3.35.0. |

---

## Project Folder Reference

### `app/` — Application Source Code

The runtime Python code. Everything Streamlit imports lives here.

| File | Role |
|---|---|
| `sidebar_app.py` | **Main entry point** for the Streamlit UI. Sidebar navigation router, product auto-detection, session state, page config. All six pages are dispatched from here. Also contains `_enrich_output_with_guide_links()` which post-processes LLM output to inject clickable guide and chapter URLs. |
| `app_functions.py` | **Engine room.** Contains `run_agent()`, `get_product_info()` (RAG search tool), `match_terms_to_guides()`, `suggest_chapters()`, `extract_doc_clues_data()`, and all scoring/matching logic. |
| `vector_store_manager.py` | **Singleton ChromaDB manager.** Handles initialization (persistent or in-memory), SQLite version detection, batch ingestion, and migration from OneDrive paths. |
| `ingestion.py` | **Document loader.** Walks `knowledge_docs/`, reads PDFs and Markdown, builds section maps from PDF headings, chunks text, and attaches product/source/section metadata. |
| `utils.py` | **LLM factory.** `get_llm()` returns a LangChain `ChatOpenAI` or `AzureChatOpenAI` depending on `CISCO_API_TYPE` env var (`cxai` or `bridgeit`). Also manages Azure auth token caching. |
| `bug2.py` | **CDETS API client.** OAuth1-authenticated calls to fetch bug summaries, notes, field values, and file attachments from `cdetsng.cisco.com`. |
| `paths.py` | **Central path registry.** Defines `PROJECT_ROOT`, `CONFIG_DIR`, `PROMPTS_DIR`, `TEMPLATES_DIR`, `INVENTORY_DIR`, `KNOWLEDGE_DOCS_DIR`, `DATA_DIR`, `ONTOLOGY_DIR`, `SCOUR_OUTPUT_DIR`, `TESTS_DIR`. Import these instead of hard-coding paths. |
| `sidebar_first_draft_page.py` | Page component: **First Draft Generation** (SFS → user guide). |
| `sidebar_bulk_analysis_page.py` | Page component: **Bulk Analysis** (Excel upload → batch ChapterFinder + ContentWriter). |
| `sidebar_resolve_bug_page.py` | Page component: **Resolve Bug** (create resolution comments, post to CDETS, send email). |
| `sidebar_hallucination_check_page.py` | Page component: **Hallucination Check** (compare original vs. AI-generated content). |
| `sidebar_admin_page.py` | Page component: **Admin** (download documentation, force-refresh HTML chapters, rebuild vector store). |

---

### `admin/` — Download Modules

Product-specific download scripts called by the Admin page. Each module exposes a `run_download()` function with a standard signature.

| File | Role |
|---|---|
| `download_sdwan_html.py` | **HTML chapter downloader.** Two-step pipeline: downloads raw HTML from cisco.com → converts to Markdown via `markdownify`. Supports `--book`, `--force`, `--reconvert`, `--dry-run`. Includes `STATIC_BOOK_OVERRIDES` for books with JS-rendered inventory URLs (e.g. `systems-interfaces-book-xe-sdwan`). |
| `download_cisco8000.py` | **Cisco 8000 HTML chapter downloader.** Three-phase pipeline: discovers books from the 8000-series support page → downloads raw HTML chapters → converts to Markdown via `markdownify`. Builds `inventory/Cisco8000/document_inventory.json`. Supports `--book`, `--force`, `--reconvert`, `--dry-run`, `--release`. Also provides `--archive` (move PDFs to `pdf_archive/`), `--validate` (compare inventory vs Markdown on disk), and `--compare` (compare archived PDFs vs Markdown book coverage). |
| `download_sdwan.py` | Legacy PDF downloader for SD-WAN guides. |
| `download_asr9000.py` | **ASR 9000 HTML chapter downloader.** Three-phase pipeline: discovers books from the ASR 9000-series support pages (config + install guides) → downloads raw HTML chapters → converts to Markdown via `markdownify`. Builds `inventory/ASR9000/document_inventory.json`. Supports `--book`, `--force`, `--reconvert`, `--dry-run`, `--release`. Also provides `--archive` (move PDFs to `pdf_archive/`), `--validate` (compare inventory vs Markdown on disk), and `--compare` (compare archived PDFs vs Markdown book coverage). |
| `download_iot.py` | PDF downloader for IoT guides. |

---

### `config/` — Configuration Files (JSON)

All behavioral tuning happens here. **No Python code changes required** for most customizations.

| File | Purpose |
|---|---|
| `app_config.json` | Persists user preferences (selected product name, tester name). Written at runtime. |
| `guide_mappings.json` | **Legacy monolithic guide mapping.** Superseded by per-product files under `ontology/<product>/guide_mappings.json`. Kept as fallback. |
| `networking_terms.json` | **Vocabulary dictionary.** ~4,000+ networking technology terms organized by category (features, protocols, hardware, etc.). The pre-extraction engine scans bug/RCA text for these terms before passing them to the LLM. |
| `product_keywords.json` | **Product auto-detection rules.** Maps each product to keywords used to auto-detect which product a bug/RCA belongs to when content is pasted. Order matters — first match wins. |

> 📖 See the [JSON Files — The Complete Reference](#json-files--the-complete-reference) section for detailed schemas and editing guides.

---

### `ontology/` — Per-Product Guide Mappings & Knowledge Graph

Product-specific and shared guide selection mappings, plus knowledge-graph data (book descriptions, chapter triples). Managed via the **Ontology** page in the UI.

```
ontology/
├── _shared/
│   └── guide_mappings.json    ← Cross-product settings (stop words, noise words, install/upgrade terms)
├── sdwan/
│   ├── guide_mappings.json    ← SD-WAN concept-to-guide map, reference guide patterns, product noise
│   └── book_kgraph.json       ← Knowledge graph: book descriptions + chapter RDF triples
├── ASR9000/
│   └── guide_mappings.json
├── Cisco8000/
│   └── guide_mappings.json
└── 9800/
    └── guide_mappings.json
```

---

### `knowledge_docs/` — Documentation Guides (Vector Store Source Material)

The raw knowledge base. Each subfolder is a **product code** containing documentation files. During ingestion, every file is chunked and embedded into ChromaDB with metadata `{product, source, book, chapter}`.

```
knowledge_docs/
├── 9800/                     ← Cisco Catalyst 9800 Wireless Controller
│   └── b_wl_17_18_cg.pdf
├── ASR9000/                  ← ASR 9000 Series Routers (Markdown chapters from HTML pipeline)
│   ├── <book-slug>/         ← One subfolder per book
│   │   ├── <chapter>.md
│   │   └── ...
│   └── ...
├── Cisco8000/                ← Cisco 8000 Series Routers (Markdown chapters from HTML pipeline)
│   ├── <book-slug>/         ← One subfolder per book (like sdwan/)
│   │   ├── <chapter>.md
│   │   └── ...
│   └── ...
├── cisco_generic/            ← Cross-product generic docs
│   └── overview.md
└── sdwan/                    ← Cisco SD-WAN (28 books, ~367 Markdown chapter files)
    ├── overview.md
    ├── appqoe-book-xe/       ← One subfolder per book
    │   ├── read-me-first.md
    │   ├── m-tcp-optimization.md
    │   └── ... (9 chapter files)
    ├── routing-book-xe/
    │   ├── m-routing-overview.md
    │   └── ... (16 chapter files)
    ├── systems-interfaces-book-xe-sdwan/   ← 66 chapters (static override)
    │   ├── etherchann.md
    │   ├── network-interfaces.md
    │   └── ... (66 chapter files)
    └── ... (28 book folders total)
```

**How sdwan/ was populated:** All 28 books are downloaded from cisco.com using `admin/download_sdwan_html.py` (accessible via the Admin tab). The pipeline downloads raw HTML, extracts `div#chapterContent`, and converts to Markdown using `markdownify`. One book (`systems-interfaces-book-xe-sdwan`) has JS-rendered inventory URLs, so it uses a static URL override that scrapes the correct TOC page. See [Knowledge Docs Pipeline](#knowledge-docs-pipeline--html--markdown-conversion) for the full workflow.

**Important:** The folder name IS the product code used throughout the application. All product-mapping dictionaries reference these exact folder names. The ingestion pipeline (`ingestion.py`) picks up `.pdf`, `.txt`, and `.md` files from these directories.

---

### `prompts/` — LLM Prompt Templates

Markdown files that define how the AI behaves for each workflow. They use `{placeholder}` syntax for variable injection via `apply_prompt_file()`.

| Prompt File | Used By | Purpose |
|---|---|---|
| `BugAnalyze.md` | Analysis & Summary page | Searches the vector store for each recommended guide, extracts metadata, and writes documentation content. |
| `ChapterFinder.md` | Analysis & Summary + Bulk Analysis | Identifies the best PDF guide and chapter location for a bug/RCA. Extracts Cisco doc URLs, determines book identifiers, and ranks locations. |
| `ContentWriter.md` | Analysis & Summary + Bulk Analysis | Given a location, writes actual documentation content (caveats, config steps, workarounds, notes). |
| `FirstDraftCTWG.md` | First Draft page | Transforms an internal SFS (Software Functional Specification) into a customer-facing user guide. Filters internal info, creates DITA-style content types (Concept, Task, Process, Reference, Principle). |
| `InternalAnalysis.md` | First Draft page (Step 1) | Scans an SFS for internal-only information (implementation logic, private APIs, debug hooks) and lists what should NOT appear in the user guide. |
| `SFSExplainer.md` | First Draft page | Creates a technical summary of an SFS document for writers unfamiliar with the feature. Uses analogies and plain language. |
| `HallucinationCheck.md` | Hallucination Check page | Compares original source content with AI-generated content. Produces a detailed report of properly sourced content, hallucinations, and missing information. |
| `summarize.md` | Analysis & Summary page | Extracts a structured bug summary (description, product, severity, root cause, workaround). |
| `ReviewYourChunks.md` | Analysis & Summary page | Reviews documentation chunks against Cisco Content Type (CT) guidelines — checks title rules, short descriptions, chunk rules, and content organization. |
| `ShortDescriptionPrompt.md` | Various | Generates `<shortdesc>` elements following information-type-specific rules. |
| `bookSD.md` | Various | Generates book-level short descriptions (2–3 sentences). |
| `chapterSD.md` | Various | Generates chapter-level short descriptions (1–2 sentences). |
| `H1SD.md` | Various | Generates H1-section-level short descriptions. |

---

### `templates/` — DITA XML Templates

Cisco Content Type (CT) structural templates used in the First Draft workflow to organize content.

| Template | Information Type | When Used |
|---|---|---|
| `ct-concept.xml` | **Concept** | Explains "what something is." Contains definition, sub-definition, and reference-info sections. |
| `ct-task.xml` | **Task** | Explains "how to do something." Contains purpose, context, prerequisites, and ordered steps. |
| `ct-process.xml` | **Process** | Explains "how something works" (system behavior). |
| `ct-principle.xml` | **Principle** | Explains guidelines, rules, or best practices. |
| `ct-reference.xml` | **Reference** | Lookup information (tables, command references). |
| `chaptermap.ditamap` | **Chapter Map** | DITA map organizing topics into a chapter hierarchy with a relationship table. |

---

### `data/` — Runtime Data & Caches

Files generated and consumed at runtime. **Do not manually edit** unless debugging.

| File | Purpose |
|---|---|
| `auth_token_cache.json` | Cached Azure/BridgeIt OAuth token with expiration timestamp. Auto-refreshes when expired. |
| `heading_cache.json` | **Extracted TOC headings** from every ingested PDF, organized by `{product_code → pdf_filename → headings[]}`. Used by `suggest_chapters()` to recommend specific chapters within a guide without re-reading the PDF. (~12,600 lines) |
| `ingestion_metadata.json` | Tracks which files have been ingested (file path, modified time, size). Used by incremental ingestion to skip unchanged files. |
| `cisco_products_custom_loader/` | Legacy vector store location (before migration to `~/.denver_vectorstore`). Kept for backward compatibility. |
| `ingestion.log` | Log output from the ingestion process. |

---

### `inventory/` — Document Inventories

Contains `document_inventory.json` files per product that map each PDF guide to its online chapters with URLs. Used to generate clickable links in the output.

```
inventory/
└── sdwan/
    └── document_inventory.json
```

**Schema** (per guide entry):
```json
{
  "appqoe-book-xe.pdf": {
    "title": "Cisco Catalyst SD-WAN AppQoE Configuration Guide...",
    "source_url": "https://www.cisco.com/c/en/us/td/docs/.../appqoe-book-xe.html",
    "chapters": [
      {
        "chapter_slug": "m-tcp-optimization",
        "chapter_title": "TCP Optimization",
        "chapter_url": "https://www.cisco.com/.../m-tcp-optimization.html"
      }
    ]
  }
}
```

When the app identifies a recommended guide and chapter, it looks up this inventory to provide a **direct clickable link** to the online documentation.

---

### `scripts/` — Standalone Utilities

Maintenance and data-preparation scripts. Run independently from the command line.

| Script | Purpose |
|---|---|
| `scour_books.py` | **Concept mapper generator.** Extracts TOC from PDF bookmarks (or text scan), sends headings to an LLM for concept/synonym extraction, cross-references against `networking_terms.json`, and outputs draft concept-to-guide mappings + a gap report of new terms. |
| `incremental_ingestion.py` | Re-ingests only new or modified files into the vector store. Compares file metadata against `ingestion_metadata.json`. |
| `_archive_downloadbooks_landing.py` | *(Archived)* Legacy SD-WAN PDF downloader — superseded by `admin/download_sdwan.py`. |
| `_archive_downloadbooks_iot_collection.py` | *(Archived)* Legacy IoT PDF downloader — superseded by `admin/download_iot.py`. |
| `extract_chapters.py` | Extracts chapter metadata from PDFs to build `document_inventory.json`. |
| `merge_scour_concepts.py` | Merges scour output from multiple runs into `guide_mappings.json`. |
| `check_bug_fields.py` | Debug utility to inspect CDETS bug field values. |
| `fetch_bug.py` | Standalone bug fetcher (CLI). |
| `Convert.py` | Converts markdown/text content to DITA XML. |
| `gen_book_descriptions.py` | **Legacy HTML chapter-text fetcher** (superseded by `admin/download_sdwan_html.py` for SD-WAN). Downloads chapter text from cisco.com HTML pages and caches each chapter as a `.txt` file. Still used for ontology/knowledge-graph generation with `--product` flag. |
| `extract_systems_interfaces_pdf.py` | **Legacy PDF chapter extractor** for `systems-interfaces-book-xe-sdwan` (superseded by the static URL override in `admin/download_sdwan_html.py`). |
| `debug_analysis.py` | **RCA analysis debugger.** Replicates the full Analysis tab flow (term detection → guide matching → prompt construction → optional LLM call) without needing Streamlit. Essential for testing RCA changes before deploying. See [Testing RCA Analysis Without Streamlit](#testing-rca-analysis-without-streamlit). |
| Other `check_*.py` / `debug_*.py` | Various diagnostic utilities. |

---

### `pdf_archive/` — Archived PDF Guides

Original PDF guides moved out of `knowledge_docs/` to prevent double-indexing in the vector store (since chapter text now lives in Markdown files). Kept as a backup. Use `admin/download_cisco8000.py --archive` to auto-move PDFs here after downloading Markdown chapters.

```
pdf_archive/
├── sdwan/
│   ├── appqoe-book-xe.pdf
│   ├── systems-interfaces-book-xe-sdwan.pdf
│   └── ... (42 PDF files)
└── Cisco8000/          ← Created by --archive flag
    ├── b-bgp-config-cisco8000.pdf
    └── ... 
```

---

### `scour_output/` and `scour_output_sdwan/` — Scour Results

Output directories for `scour_books.py` runs.

| File | Contents |
|---|---|
| `draft_concept_mappings.json` | Extracted concept → guide pattern mappings ready to merge into `guide_mappings.json`. |
| `gap_report_new_terms.json` | Terms found in PDF TOCs that don't yet exist in `networking_terms.json`. Add these to expand the vocabulary. |
| `raw_results.json` | Full LLM output for each book processed. |
| `summary.txt` | Human-readable summary (books processed, headings found, concepts extracted). |
| `*.log` | Execution logs. |

---

### `tests/` — Test Suite

| File | Purpose |
|---|---|
| `test_all_models.py` | Tests all LLM model configurations. |
| `test_component_field.py` | Tests component field extraction logic. |
| `test_models.py` | Tests individual model behavior. |
| `test_post_resolution.py` | Tests the bug resolution posting workflow. |
| `test_gen_book_descriptions.py` | Tests the HTML chapter-text fetch pipeline (cache, HTML fetch, 404 handling, inventory loading). 16 tests. |
| `testresults.xlsx` | Aggregated test results from the in-app testing framework. |

---

### `legacy/` — Previous Versions

Contains the original tab-based Streamlit app (`streamlit_app.py`) before the sidebar navigation redesign. Kept for reference.

---

### `docker/` — Container Deployment

| File | Purpose |
|---|---|
| `Dockerfile` | Multi-stage build for the Denver app. |
| `docker-compose.yml` | Development compose configuration. |
| `docker-compose.prod.yml` | Production compose configuration. |
| `.env` / `.env.example` | Environment variable templates. |
| `DOCKER_GUIDE.md` | Plain-English Docker setup guide. |

---

### `taxonomy/` — Static Documentation Taxonomy *(New)*

Writer-reviewable, hierarchical maps of every book/chapter/section tagged with networking concepts. Generated by `scripts/build_taxonomy.py`. See [Taxonomy — Static Documentation Map](#taxonomy--static-documentation-map) for full details.

| Path | Purpose |
|---|---|
| `taxonomy/<product>/taxonomy.json` | One taxonomy file per product (sdwan, ASR9000, Cisco8000, 9800). |

---

## Application Entry Points

There are two ways to start the app:

### 1. Via `start.py` (Recommended)

```bash
python start.py
```

This script:
1. Pre-initializes the vector store (loads all PDFs into ChromaDB)
2. Launches Streamlit pointing at `app/sidebar_app.py`
3. Provides startup feedback and error handling

### 2. Direct Streamlit Launch

```bash
streamlit run app/sidebar_app.py
```

The app auto-initializes the vector store on first load if it hasn't been initialized.

---

## The Six App Pages

### 🔍 Analysis & Summary
- **Input:** CDETS bug number(s) or pasted RCA content
- **Process:** Fetches bug from CDETS → auto-detects product → scans for networking terms → matches terms to guides → scores and ranks guides → sends to LLM with RAG search
- **Output:** Top-3 guide recommendations with chapter suggestions, documentation content, and clickable online links (both guide-level and chapter-level URLs are injected by `_enrich_output_with_guide_links()`)

### ✍️ First Draft
- **Input:** Uploaded SFS document(s) (.txt, .md, .docx, .pdf)
- **Process:** Step 1: Identifies internal information → Step 2: Generates customer-facing user guide
- **Output:** DITA-structured documentation using Concept/Task/Process/Reference/Principle types

### 📊 Bulk Analysis
- **Input:** Excel file with RCA text or bug numbers in a column
- **Process:** Iterates through each row, runs ChapterFinder → ContentWriter pipeline
- **Output:** Enriched Excel file with Top-3 recommendations and AI analysis per row

### 🔧 Resolve Bug
- **Input:** CDETS bug number + change description + impacted chapters
- **Process:** Fetches bug metadata → generates resolution comment → posts to CDETS → sends notification email
- **Output:** Resolution comment posted to CDETS + email to submitter

### 🔍 Hallucination Check
- **Input:** Original source content + AI-generated/modified content
- **Process:** Compares both versions, identifies fabricated information, missing content, and properly sourced content
- **Output:** Detailed hallucination detection report with severity ratings

### 🛠️ Admin
- **Input:** Product selection, optional force-refresh checkbox
- **Process:** Downloads documentation from cisco.com (HTML chapters for SD-WAN, PDFs for other products), converts HTML to Markdown. Can also rebuild the ChromaDB vector store from the current `knowledge_docs/` contents.
- **Key files:** `sidebar_admin_page.py` (UI), `admin/download_sdwan_html.py` (SD-WAN HTML→Markdown pipeline)
- **Output:** Updated Markdown files in `knowledge_docs/`, rebuilt vector store

---

## JSON Files — The Complete Reference

### `config/product_keywords.json` — Product Auto-Detection

**What it does:** When a user pastes bug/RCA content, the app scans it for these keywords to automatically select the correct product in the UI dropdown. First match wins.

**Schema:**
```json
{
  "_comment": "Maps product names to keyword lists. Order matters: first match wins.",
  "products": [
    {
      "name": "Cisco SD-WAN",           // ← Must match the UI selectbox option exactly
      "keywords": [
        "sd-wan", "sdwan", "vmanage",   // ← Case-insensitive substring match
        "vedge", "cedge", "vbond"
      ]
    }
  ]
}
```

**To edit:** Add keywords that uniquely identify a product. Place more specific products first (e.g., "ASR 9000" before "cisco_generic").

---

### `config/networking_terms.json` — Vocabulary Dictionary

**What it does:** The pre-extraction engine (`_scan_for_networking_terms()`) scans bug/RCA content for these terms. Matched terms are then used to:
1. Select which PDF guides are most relevant
2. Suggest which chapters within those guides to search
3. Provide search keywords to the LLM agent

**Schema:**
```json
{
  "_comment": "Networking technology terms. Add your own terms here!",
  "features": [
    "segment routing",
    "bgp",
    "application-aware routing",
    "appqoe controller"
  ],
  "protocols": [ "ospf", "isis", "mpls", "bfd" ],
  "hardware": [ "a99-rsp", "asr9903", "ncs 5500" ]
}
```

**Categories** are organizational only — all terms from all categories are scanned equally. Terms are **case-insensitive** and matched using word boundary regex.

**To edit:** Add new terms in lowercase. Multi-word terms (e.g., "segment routing") are preferred because they get higher scoring weight (2.0× vs 0.5× for single words).

---

### `config/guide_mappings.json` — The Guide Selection Brain

**What it does:** This is the most important configuration file. It controls how detected technology terms are mapped to specific PDF guides. It has several sections:

#### Section 1: `reference_guides`
Guides that are **excluded from scoring** because they match too many terms (e.g., alarm indexes). Users can still manually select them.

```json
"reference_guides": {
  "patterns": {
    "sdwan": ["alarms-guide"],
    "ASR9000": ["rcsi-0350", "asr9k-overview-reference", "vsmig"]
  }
}
```

#### Section 2: `install_upgrade_terms`
When any of these terms are detected, install/upgrade guides are automatically included.

```json
"install_upgrade_terms": {
  "terms": ["upgrade", "install", "firmware", "boot", "rommon", "issu"],
  "guide_patterns": ["install", "upgrade", "setup", "-hig", "gs-book"]
}
```

#### Section 3: `concept_to_guide` — The Core Mapping

**This is the heart of the system.** It maps technology concepts (that may NOT literally appear in a guide filename) to filename patterns of guides that cover that concept.

```json
"concept_to_guide": {
  "sdwan": {
    "_comment": "When term (key) is detected, guides with these filename patterns (values) are selected.",
    "certificate": ["security", "sdwan-xe-gs", "system-security"],
    "troubleshoot": ["maintain", "monitor", "monitor-maintain", "troubleshoot"],
    "deployment": ["compatibility", "configuration-group", "maintain", "monitor"],
    "ospf": ["routing"],
    "bgp": ["routing"],
    "qos map": ["configuration-group", "qos", "modular-qos"]
  },
  "ASR9000": {
    "cnbng": ["cnbng-user-plane"],
    "bng": ["bng-cg"],
    "segment routing": ["segment-routing"]
  }
}
```

**Why this matters:** The term "certificate" never appears in a guide filename, but it belongs in the Security guide and the Getting Started guide. This mapping bridges that semantic gap.

#### Section 4: `product_noise` / `filename_noise_words` / `stop_words`
Noise filtering to prevent generic terms from matching every guide.

---

### `data/heading_cache.json` — PDF Table-of-Contents Cache

**What it does:** Stores extracted TOC headings from every PDF guide. Used by `suggest_chapters()` to recommend specific chapters within a guide.

**Schema:**
```json
{
  "sdwan": {
    "appqoe-book-xe.pdf": {
      "headings": [
        "Cisco Catalyst SD-WAN AppQoE Configuration Guide...",
        "TCP Optimization",
        "Configure AppQoE Controllers and Service Nodes...",
        "Monitor AppQoE Service Controllers and Nodes"
      ]
    }
  }
}
```

**Generated by:** `scour_books.py` or during ingestion. **Do not manually edit** — regenerate using the scour script.

---

### `data/ingestion_metadata.json` — Ingestion Tracker

**What it does:** Records which files have been ingested and their last-modified timestamps. The incremental ingestion script uses this to skip unchanged files.

```json
{
  "/path/to/knowledge_docs/sdwan/policies-book-xe.pdf": {
    "modified_time": 1769091019.03,
    "size": 28601703,
    "last_check": "2026-02-11T15:41:23.802357"
  }
}
```

---

### `data/auth_token_cache.json` — OAuth Token Cache

**What it does:** Caches the Azure/BridgeIt OAuth access token with a 1-hour expiration to avoid re-authenticating on every API call.

```json
{
  "token": "eyJ0...",
  "expiration": "2026-03-09T15:30:00.000000"
}
```

---

### `inventory/<product>/document_inventory.json` — Online Chapter URLs

**What it does:** Maps each PDF guide to its online source URL and individual chapter URLs. When the app identifies "policies-book-xe.pdf, Chapter: TCP Optimization", it looks here to generate a clickable link.

```json
{
  "appqoe-book-xe.pdf": {
    "title": "Cisco Catalyst SD-WAN AppQoE Configuration Guide...",
    "source_url": "https://www.cisco.com/.../appqoe-book-xe.html",
    "chapters": [
      {
        "chapter_slug": "m-tcp-optimization",
        "chapter_title": "TCP Optimization",
        "chapter_url": "https://www.cisco.com/.../m-tcp-optimization.html"
      }
    ]
  }
}
```

---

### `scour_output/draft_concept_mappings.json` — Scour Results

**What it does:** Output from `scour_books.py`. Contains extracted concept terms for each product, ready to be merged into `guide_mappings.json`.

---

### `scour_output/gap_report_new_terms.json` — Vocabulary Gaps

**What it does:** Lists terms found in PDF TOCs that don't yet exist in `networking_terms.json`. Review and add relevant terms to expand the vocabulary.

---

## Concept-to-Topic Mapping: How It Works

This is the core intelligence of the Denver app. Here is the full pipeline, step by step:

### Step 1: Term Detection
When a user pastes bug/RCA content, `_scan_for_networking_terms()` in `app_functions.py`:
1. Loads the vocabulary from `config/networking_terms.json`
2. Scans the text using word-boundary regex (case-insensitive)
3. Creates a normalized version (underscores/hyphens → spaces) to catch component fields like `cnbng_nal`
4. Returns a list of `(category, term)` tuples and a frequency dictionary `{term: count}`

### Step 2: Guide Matching
`match_terms_to_guides()` takes the detected terms and:

1. **Direct filename matching:** If the term appears as a substring in a PDF filename, it's a match (e.g., `"bgp"` matches `b-bgp-config-cisco8000.pdf`)
2. **Install/upgrade injection:** If install-related terms are detected, install/upgrade guides are auto-added
3. **Concept-to-guide mapping:** Looks up `guide_mappings.json → concept_to_guide → {product}` to find guides for terms that don't appear in filenames (e.g., `"certificate"` → `security-book-xe.pdf`)

### Step 3: Scoring
Each matched guide receives a weighted score based on:

| Factor | Weight | Purpose |
|---|---|---|
| **Inverse breadth** | `1/num_guides` | A term matching 1 guide scores higher than one matching 5 guides |
| **Frequency boost** | `log₂(freq) + 1`, capped at 3.0 | Terms mentioned 8× matter more than terms mentioned once |
| **Specificity bonus** | 2.0× for multi-word terms | "segment routing" is more informative than "routing" |
| **Diminishing returns** | `score^0.7` | Prevents "catch-all" guides from dominating by accumulating many low-value terms |

Reference-only guides (from `reference_guides` config) are excluded from scoring.

### Step 4: Chapter Suggestion
`suggest_chapters()` uses the `heading_cache.json` to:
1. Load all TOC headings for the matched guide
2. Score each heading by counting how many matched terms appear as substrings
3. Down-weight ubiquitous terms that appear in the book title or >60% of headings
4. Return the top-5 most relevant chapter headings

### Step 5: Inventory Lookup
`find_inventory_chapter()` maps a suggested heading back to the nearest parent chapter in `document_inventory.json`, providing the `chapter_url` for a clickable link.

### The Flow Diagram

```
Bug/RCA Text
    │
    ▼
networking_terms.json ──► _scan_for_networking_terms()
    │                          │
    │                    detected_terms + frequencies
    │                          │
    ▼                          ▼
guide_mappings.json ────► match_terms_to_guides()
    │                          │
    │                    matched_guides + scores
    │                          │
    ▼                          ▼
heading_cache.json ─────► suggest_chapters()
    │                          │
    │                    top chapter headings
    │                          │
    ▼                          ▼
document_inventory.json ► find_inventory_chapter()
    │                          │
    │                    chapter URLs (clickable links)
    │                          │
    ▼                          ▼
                        LLM Agent + RAG Search
                               │
                        Final Recommendations
```

---

## Adding a New Product — Step-by-Step

Follow these steps to add support for a new Cisco product (e.g., "Cisco NCS 540"):

### Step 1: Create the Knowledge Docs Folder

Create a subfolder under `knowledge_docs/` with your **product code** as the folder name:

```bash
mkdir knowledge_docs/NCS540
```

Place all relevant PDF guides into this folder. Markdown (`.md`) files are also supported.

> **Product code naming convention:** Use a short, filesystem-safe name with no spaces. This code will be referenced everywhere.

### Step 2: Add Product Keywords for Auto-Detection

Edit `config/product_keywords.json` and add a new entry in the `products` array:

```json
{
  "name": "Cisco NCS 540",
  "keywords": [
    "ncs 540", "ncs540", "ncs-540",
    "ncs 5xx", "540-series"
  ]
}
```

> **Important:** The `name` field must match the exact string you'll add to the product selectbox in the UI.

### Step 3: Register the Product in the UI

In `app/sidebar_app.py`, find the `product_options` list and add your product:

```python
product_options = ["Cisco SD-WAN", "Cisco 9800", "ASR 9000", "Cisco 8000", "Cisco NCS 540", "cisco_generic"]
```

### Step 4: Add the Product Mapping

The product mapping dictionary appears in **multiple files**. Search for `product_mapping` and add your entry everywhere:

```python
product_mapping = {
    "Cisco SD-WAN": "sdwan",
    "Cisco 9800": "9800",
    "ASR 9000": "ASR9000",
    "Cisco 8000": "Cisco8000",
    "Cisco NCS 540": "NCS540",       # ← Add this
    "cisco_generic": "cisco_generic"
}
```

**Files that contain `product_mapping`:**
- `app/sidebar_app.py` — `get_available_guides()` and `_enrich_output_with_guide_links()`
- `app/app_functions.py` — `match_terms_to_guides()`, `suggest_chapters()`, `find_inventory_chapter()`, `load_document_inventory()`
- `app/vector_store_manager.py` — (if adding product-specific collection logic)

> **Tip:** Use your IDE's global search for `product_mapping` to find all instances.

### Step 5: Add Networking Terms (Optional but Recommended)

Edit `config/networking_terms.json` and add terms specific to your product. This dramatically improves guide selection accuracy.

```json
{
  "features": [
    "ncs 540",
    "ios xr",
    "segment routing",
    ...existing terms plus new product-specific ones...
  ]
}
```

### Step 6: Create Concept-to-Guide Mappings

Edit `config/guide_mappings.json` and add a new product section under `concept_to_guide`:

```json
"concept_to_guide": {
  "sdwan": { ... },
  "ASR9000": { ... },
  "NCS540": {
    "segment routing": ["segment-routing"],
    "bgp": ["routing"],
    "troubleshoot": ["system-management", "system-monitoring"],
    "acl": ["security"]
  }
}
```

**Shortcut:** Run `scour_books.py` to auto-generate these mappings:

```bash
python scripts/scour_books.py --product NCS540
```

This extracts TOCs from your PDFs, sends them to an LLM for concept extraction, and outputs draft mappings to `scour_output/`.

### Step 7: Build the Document Inventory (Optional but Recommended)

Create `inventory/NCS540/document_inventory.json` with the online URLs for each guide and its chapters. This enables clickable links in the output.

```bash
mkdir -p inventory/NCS540
```

Then populate with:
```json
{
  "b-routing-cg-ncs540-25xx.pdf": {
    "title": "Routing Configuration Guide for Cisco NCS 540...",
    "source_url": "https://www.cisco.com/c/en/us/td/docs/...",
    "chapters": [
      {
        "chapter_slug": "bgp-config",
        "chapter_title": "Configure BGP",
        "chapter_url": "https://www.cisco.com/.../bgp-config.html"
      }
    ]
  }
}
```

Use `scripts/extract_chapters.py` to auto-extract this data.

### Step 8: Build the Heading Cache

Run `scour_books.py` to extract TOC headings for chapter suggestions:

```bash
python scripts/scour_books.py --product NCS540
```

The headings are saved to `data/heading_cache.json` under your product code.

### Step 9: Re-ingest the Vector Store

Run the ingestion to embed your new PDFs:

```bash
python scripts/incremental_ingestion.py
```

Or restart the app (it auto-ingests on startup if the vector store doesn't contain the new files).

### Step 10: Add Reference Guide Exclusions (Optional)

If your product has "catch-all" reference guides (alarm indexes, overview guides), add them to the `reference_guides` section in `guide_mappings.json`:

```json
"reference_guides": {
  "patterns": {
    "NCS540": ["overview-reference", "alarms-index"]
  }
}
```

### Verification Checklist

- [ ] PDFs placed in `knowledge_docs/NCS540/`
- [ ] Product keywords added to `config/product_keywords.json`
- [ ] Product added to `product_options` list in `sidebar_app.py`
- [ ] `product_mapping` updated in all files (search for `product_mapping`)
- [ ] Concept-to-guide mappings added to `config/guide_mappings.json`
- [ ] (Optional) Networking terms added to `config/networking_terms.json`
- [ ] (Optional) Document inventory created at `inventory/NCS540/document_inventory.json`
- [ ] (Optional) Heading cache built via `scour_books.py`
- [ ] (Optional) Reference guide exclusions added
- [ ] Vector store re-ingested
- [ ] App restarted and tested with a sample bug for the new product

---

## Prompt Templates

All prompts live in `prompts/` as Markdown files. They use `{placeholder}` variables that get replaced at runtime by `apply_prompt_file()`.

### Common Placeholders

| Placeholder | Injected With |
|---|---|
| `{rca_content}` | The bug/RCA text pasted or fetched by the user |
| `{product_name}` | The selected product name (e.g., "Cisco SD-WAN") |
| `{extracted_text}` | Content from uploaded SFS documents |
| `{selected_guides}` | Comma-separated list of guides the user selected |
| `{model_name}` | The LLM model being used |

### Editing Prompts

Simply edit the `.md` file. No code changes needed. The prompt is read fresh on each invocation.

---

## DITA XML Templates

The `templates/` folder contains Cisco Content Type (CT) DITA templates. These are used as structural guidance in the First Draft workflow:

| Template | Title Formula | Content Structure |
|---|---|---|
| `ct-concept.xml` | Plural form of the subject | Definition → Reference-info → Tables |
| `ct-task.xml` | Imperative verb + article + subject | Purpose → Context → Prerequisites → Steps |
| `ct-process.xml` | How [subject] works | Trigger → Steps → Outcome |
| `ct-principle.xml` | Guidelines/Rules | Statement → Rationale → Examples |
| `ct-reference.xml` | Descriptive noun phrase | Tables → Code blocks → Parameters |
| `chaptermap.ditamap` | Chapter title | Topic hierarchy + relationship table |

---

## Taxonomy — Static Documentation Map

The **taxonomy** is a writer-reviewable, hierarchical map of every book, chapter, and section in the documentation library — tagged with networking concepts.

### Why

The existing concept-to-chapter resolution is a 3-step runtime chain:
1. Bug concepts → guide filename (via `guide_mappings.json`)
2. Guide + terms → chapter heading (via `suggest_chapters()` + `heading_cache.json`)
3. Chapter heading → URL (via `document_inventory.json`)

The taxonomy **collapses all three steps into a single static lookup** that writers can review, edit, and trust.

### Folder Structure

```
taxonomy/
├── sdwan/
│   └── taxonomy.json          # One file per product
├── ASR9000/
│   └── taxonomy.json
├── Cisco8000/
│   └── taxonomy.json
└── 9800/
    └── taxonomy.json
```

### Schema

Each `taxonomy.json` looks like:

```json
{
  "_comment": "Auto-generated. Writers: review and edit concept tags, then commit.",
  "_product": "sdwan",
  "_book_count": 29,
  "books": [
    {
      "filename": "routing-book-xe.pdf",
      "title": "Cisco Catalyst SD-WAN Routing Configuration Guide",
      "source_url": "https://www.cisco.com/...",
      "toc_method": "bookmarks",
      "chapters": [
        {
          "title": "Configure BGP Routing",
          "chapter_url": "https://...",
          "chapter_slug": "configure-bgp-routing",
          "concepts": ["bgp", "autonomous system", "routing"],
          "sections": [
            {
              "title": "Configure eBGP Neighbors",
              "concepts": ["ebgp", "bgp neighbor"]
            },
            {
              "title": "Route Redistribution",
              "concepts": ["route redistribution", "redistribute"]
            }
          ]
        }
      ]
    }
  ]
}
```

### How to Generate

```bash
# All products — mechanical tagging only (fast, no LLM)
python scripts/build_taxonomy.py --dry-run

# All products — with LLM concept enrichment
python scripts/build_taxonomy.py

# One product
python scripts/build_taxonomy.py --product sdwan

# One specific book
python scripts/build_taxonomy.py --product sdwan --book routing-book-xe.pdf

# Use a different model
python scripts/build_taxonomy.py --model gpt-4.1
```

### The Generation Pipeline

1. **Extract TOC** — Reads PDF bookmarks (hierarchical) or falls back to text-scan.
2. **Build tree** — Nests flat headings into a Book → Chapter → Section hierarchy.
3. **Mechanical tagging** — Matches every heading against `networking_terms.json` (~4000 terms) using word-boundary regex.
4. **LLM enrichment** (optional) — Sends each chapter's headings to the LLM for deeper concept extraction (abbreviations, synonyms, sub-protocols).
5. **URL attachment** — Merges `chapter_url` and `chapter_slug` from `document_inventory.json`.
6. **Write output** — Saves to `taxonomy/<product>/taxonomy.json`.

### Writer Workflow

1. Run the script once (or when PDFs change).
2. Open `taxonomy/<product>/taxonomy.json` in any editor.
3. Review the `concepts` arrays — add missing terms, remove noise.
4. Commit the file alongside `knowledge_docs/`.
5. The app consumes the static file instead of computing matches at runtime.

> 💡 The taxonomy lives **outside Docker** — treat it the same way you treat `knowledge_docs/`.

---

## Scripts & Utilities

### `build_taxonomy.py` — Static Documentation Taxonomy Builder

Generates the hierarchical, concept-tagged taxonomy. See [Taxonomy — Static Documentation Map](#taxonomy--static-documentation-map) above.

### `scour_books.py` — The Concept Mapper

The most important maintenance script. Run it when adding new products or PDFs.

```bash
# Scour all products
python scripts/scour_books.py

# Scour one product
python scripts/scour_books.py --product sdwan

# Scour one specific book
python scripts/scour_books.py --book routing-book-xe.pdf

# Dry run (extract TOCs only, no LLM)
python scripts/scour_books.py --dry-run

# Use a specific model
python scripts/scour_books.py --model gpt-4.1
```

**Output:** `scour_output/` or `scour_output_<product>/` containing draft mappings, gap reports, and summaries.

### `incremental_ingestion.py` — Smart Re-ingestion

Only processes new or modified files. Compares `ingestion_metadata.json` timestamps.

```bash
python scripts/incremental_ingestion.py
```

---

## Knowledge Docs Pipeline — HTML & Markdown Conversion

The `knowledge_docs/sdwan/` folder is populated with Markdown chapter files converted from Cisco's online HTML documentation. This provides high-fidelity text for the RAG vector store — headings, tables, lists, and code blocks are preserved as Markdown structure rather than being flattened to plain text.

### How It Works

1. **Inventory** — `inventory/sdwan/document_inventory.json` lists all 28 books with their chapter slugs, titles, and cisco.com URLs.
2. **Static overrides** — Some books (e.g. `systems-interfaces-book-xe-sdwan`) have JS-rendered inventory URLs that return empty shells. The `STATIC_BOOK_OVERRIDES` dict in `admin/download_sdwan_html.py` maps these to a working static TOC URL. The override scrapes the real chapter list from the Cisco.com sidebar.
3. **HTML download** — `admin/download_sdwan_html.py` fetches each chapter page, saves the raw HTML to `data/html_archive/sdwan/<book>/<chapter>.html`.
4. **Markdown conversion** — The same script extracts `div#chapterContent` using BeautifulSoup and converts it to Markdown via `markdownify`. Output goes to `knowledge_docs/sdwan/<book>/<chapter>.md`.
5. **Ingestion** — The existing `app/ingestion.py` pipeline walks `knowledge_docs/` and ingests all `.md`, `.txt`, and `.pdf` files into ChromaDB.

### Running the Pipeline

From the **Admin tab** in the Streamlit UI:
1. Select **"Cisco SD-WAN (HTML Chapters)"** from the Product dropdown
2. Optionally check **"Force refresh"** to re-download all chapters
3. Click **"Start Download"**
4. After download completes, use the **"Rebuild Vector Store"** button to re-ingest

From the **command line**:

```bash
# Download all books (skips existing files)
python -m admin.download_sdwan_html

# Download a single book
python -m admin.download_sdwan_html --book routing-book-xe

# Force re-download everything
python -m admin.download_sdwan_html --force

# Re-convert cached HTML to Markdown (no download)
python -m admin.download_sdwan_html --reconvert

# Preview what would be fetched
python -m admin.download_sdwan_html --dry-run
```

### Current Coverage

| Source | Books | Chapter Files | Notes |
|---|---|---|---|
| Inventory (standard) | 27 | ~301 | Fetched from cisco.com chapter pages |
| Static override | 1 | 66 | `systems-interfaces-book-xe-sdwan` (static TOC scrape) |
| **Total** | **28** | **~367** | All inventory books covered |

### File Layout

```
data/html_archive/sdwan/          ← Raw HTML backup (source of truth)
├── appqoe-book-xe/
│   ├── read-me-first.html
│   └── ...
└── systems-interfaces-book-xe-sdwan/
    ├── etherchann.html
    └── ...

knowledge_docs/sdwan/             ← Markdown for ingestion
├── overview.md
├── appqoe-book-xe/
│   ├── read-me-first.md
│   └── ...
├── systems-interfaces-book-xe-sdwan/
│   ├── etherchann.md
│   └── ...
└── ...
```

### Key Constants (in `admin/download_sdwan_html.py`)

| Constant | Value | Purpose |
|---|---|---|
| `REQUEST_TIMEOUT` | 30s | HTTP request timeout |
| `DELAY_BETWEEN` | 0.3s | Rate-limit delay between web requests |
| `MIN_CONTENT_CHARS` | 2,000 | Below this threshold → likely JS-rendered shell |
| `HTTP_RETRIES` | 2 | Retry count for failed HTTP requests |

### Chapter URL Enrichment

When the LLM produces Location Recommendations, `_enrich_output_with_guide_links()` in `sidebar_app.py` post-processes the output to inject clickable links:

- **Guide-level link** — Added after each `Document name:` line (looked up from `document_inventory.json`)
- **Chapter-level link** — Added after each `Chapter:` line (looked up from inventory chapters, or constructed from `_STATIC_CHAPTER_BASES` for override books)

This means the user sees direct cisco.com links to both the guide homepage and the specific chapter referenced in each recommendation.

---

## Testing RCA Analysis Without Streamlit

`scripts/debug_analysis.py` replicates the full Analysis tab pipeline (term detection → guide matching → prompt construction → optional LLM call) from the command line. Use it to verify changes to the analysis logic without launching Streamlit.

### Quick Start

```bash
cd Denver2

# Run with built-in QoS shaping RCA (pipeline only, no LLM):
python3 scripts/debug_analysis.py --rca qos_shaping --no-llm

# Run with LLM call:
python3 scripts/debug_analysis.py --rca qos_shaping

# Default RCA (mss_clamping):
python3 scripts/debug_analysis.py --no-llm
```

### Available Test RCAs

| Key | Product | Description |
|---|---|---|
| `mss_clamping` | Cisco SD-WAN | TCP MSS Clamping on cEdge C8300 (default) |
| `template` | Cisco SD-WAN | Feature template negotiation failure on vEdge |
| `policy` | Cisco SD-WAN | Centralized data policy not applying to traffic |
| `qos_shaping` | Cisco SD-WAN | QoS Shaping Rate configuration guidance on C8200 |

Additional RCAs are defined in the `TEST_RCAS` dict at the top of the script — add new ones as needed.

### What It Traces (8 Steps)

1. **Term Detection** — networking terms + URL clues extracted from RCA text
2. **Guide Matching & Scoring** — terms matched against guide mappings, scores computed
3. **run_agent() Replacement Logic** — `{{RECOMMENDED_GUIDE}}` and `{{RECOMMENDED_SECTION}}` resolved
4. **Key Lines the LLM Sees** — shows the final prompt lines with replacements applied
5. **full_question Construction** — prompt template + RCA content combined
6. **Agent Prompt** — the complete prompt that would be sent to the LLM, including pinned location recommendations and search scope
7. **LLM Call** *(skipped with `--no-llm`)* — actual call to `run_agent()` with mocked `st.session_state`
8. **LLM Output** *(skipped with `--no-llm`)* — shows the model's response and checks recommended guide/section

### Flags

- `--rca <key>` — select a test RCA (default: `mss_clamping`)
- `--no-llm` — skip the LLM call; traces the pipeline only

---

## Docker Deployment

See `docker/DOCKER_GUIDE.md` for the full guide. Quick start:

```bash
cd docker
docker-compose up --build
```

Environment variables go in `docker/.env` (copy from `.env.example`).

---

## Environment Variables

Set these in a `.env` file at the project root or in `docker/.env`:

| Variable | Required | Purpose |
|---|---|---|
| `CISCO_API_TYPE` | Yes | `cxai` or `bridgeit` — selects the LLM provider |
| `OPENAI_API_BASE` | If cxai | Base URL for the CX-AI OpenAI-compatible endpoint |
| `OPENAI_API_KEY` | If cxai | API key for CX-AI |
| `BRIDGEIT_CLIENT_ID` | If bridgeit | OAuth client ID for BridgeIt |
| `BRIDGEIT_CLIENT_SECRET` | If bridgeit | OAuth client secret for BridgeIt |
| `BRIDGEIT_APP_KEY` | If bridgeit | Application key for BridgeIt |
| `BRIDGEIT_BRAIN_USER_ID` | If bridgeit | Brain user ID for BridgeIt |
