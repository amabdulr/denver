# Denver — Project File Manifest

> **Purpose**: Lists every file needed to run the Denver Bug Doctor app in a
> fresh git repository. Use this as a checklist when setting up a new clone.

---

## Quick Start

```bash
# 1. Clone the repo
git clone <repo-url> && cd denver

# 2. Create a virtual environment and install dependencies
python3 -m venv myenv && source myenv/bin/activate
pip install -r requirements.txt

# 3. Create a .env file with your API keys (see "Environment" section below)

# 4. Ingest knowledge docs into the vector store
python3 ingestion.py            # full rebuild
python3 incremental_ingestion.py  # or incremental update

# 5. Launch the app
python3 start.py                # recommended (pre-loads vector store)
# — or —
streamlit run sidebar_app.py    # direct launch
```

---

## Dependency Graph (simplified)

```
start.py
  └─→ vector_store_manager.py ─→ ingestion.py ─→ knowledge_docs/**
  └─→ streamlit run sidebar_app.py
        ├─→ app_functions.py
        │     ├─→ utils.py ─→ .env (API keys)
        │     ├─→ vector_store_manager.py
        │     ├─→ networking_terms.json
        │     ├─→ guide_mappings.json
        │     ├─→ data/heading_cache.json
        │     └─→ inventory/*/document_inventory.json
        ├─→ bug2.py  (CDETS API)
        ├─→ sidebar_first_draft_page.py
        │     └─→ SFSExplainer.md, InternalAnalysis.md, FirstDraftCTWG.md
        ├─→ sidebar_bulk_analysis_page.py
        │     └─→ ChapterFinder.md, ContentWriter.md, BugAnalyze.md
        ├─→ sidebar_resolve_bug_page.py
        │     └─→ bug2.py
        ├─→ sidebar_hallucination_check_page.py
        │     └─→ HallucinationCheck.md
        ├─→ BugAnalyze.md, summarize.md  (Analysis & Summary page)
        ├─→ product_keywords.json
        └─→ app_config.json

debug_analysis.py  (standalone CLI)
  └─→ app_functions.py  (same deps above, minus Streamlit UI)

incremental_ingestion.py  (standalone CLI)
  └─→ ingestion.py ─→ knowledge_docs/**
  └─→ data/ingestion_metadata.json
```

---

## 1 · Python Source Files

### Core Application

| File | Lines | Description |
|------|------:|-------------|
| `sidebar_app.py` | 1706 | **Main Streamlit app** — sidebar navigation, Analysis & Summary page, product auto-detect, conversation history |
| `app_functions.py` | 1764 | **Engine room** — RAG search, LangChain agent orchestration, prompt template engine, guide matching |
| `utils.py` | 130 | LLM factory — creates Azure BridgeIt or CXAI `ChatOpenAI` instances |
| `bug2.py` | 406 | CDETS API client — OAuth1 auth, bug fetch, note CRUD, XML parsing |
| `vector_store_manager.py` | 259 | Singleton ChromaDB manager — auto-detects SQLite version, handles persistent vs in-memory mode |
| `ingestion.py` | 381 | Document loader & chunker — reads PDFs/MDs from `knowledge_docs/`, builds ChromaDB embeddings |
| `start.py` | 66 | Unified launcher — pre-loads vector store then starts Streamlit |

### Sidebar Page Modules (imported by `sidebar_app.py`)

| File | Lines | Description |
|------|------:|-------------|
| `sidebar_first_draft_page.py` | 643 | **First Draft** page — upload SFS docs, find internal info, generate customer-facing drafts |
| `sidebar_bulk_analysis_page.py` | 1321 | **Bulk Analysis** page — Excel upload, batch RCA processing, bug column processing |
| `sidebar_resolve_bug_page.py` | 563 | **Resolve Bug** page — CDETS integration, resolution notes, email to submitter |
| `sidebar_hallucination_check_page.py` | 266 | **Hallucination Check** page — compare original vs AI-generated content |

### Legacy Tab Modules (imported by `streamlit_app.py`)

> These are the older tab-based versions. Include them if you also want to
> run the original `streamlit_app.py`.

| File | Lines | Description |
|------|------:|-------------|
| `streamlit_app.py` | 1365 | Original tab-based Streamlit app |
| `streamlit_app_sidebar_nav.py` | 230 | Sidebar navigation demo / prototype |
| `first_draft_tab.py` | 224 | First Draft tab (old) |
| `bulk_analysis_tab.py` | 481 | Bulk Analysis tab (old) |
| `hal_check_tab.py` | 229 | Hallucination Check tab (old) |
| `Convert.py` | 158 | XML/DITA conversion tab — reads templates from `templates/` |

### Standalone CLI Tools

| File | Lines | Description |
|------|------:|-------------|
| `debug_analysis.py` | 1041 | CLI debug tool — replays Analysis tab logic without Streamlit |
| `incremental_ingestion.py` | 289 | Incremental vector store updater — only processes new/modified files |

---

## 2 · Prompt Files (Markdown)

These `.md` files are **LLM prompt templates** loaded at runtime by
`app_functions.apply_prompt_file()`. Placeholders like `{{RCA_TEXT}}`
are filled in before being sent to the model.

### Root-Level Prompts

| File | Used By | Purpose |
|------|---------|---------|
| `BugAnalyze.md` | Analysis & Summary page, Bulk Analysis | Main bug/RCA analysis prompt |
| `summarize.md` | Analysis & Summary page | Summarize analysis output |
| `SFSExplainer.md` | First Draft page | Explain SFS content |
| `InternalAnalysis.md` | First Draft page | Detect internal-only information |
| `FirstDraftCTWG.md` | First Draft page | Generate customer-facing first draft |
| `HallucinationCheck.md` | Hallucination Check page | Compare original vs modified content |
| `ChapterFinder.md` | Bulk Analysis page | RAG-based chapter/guide suggestion |
| `ContentWriter.md` | Bulk Analysis page | Generate content from RCA |
| `ShortDescriptionPrompt.md` | Auxiliary | Short description generation |

### `prompts/` Directory

| File | Purpose |
|------|---------|
| `prompts/bookSD.md` | Book-level short description prompt |
| `prompts/chapterSD.md` | Chapter-level short description prompt |
| `prompts/H1SD.md` | H1-level short description prompt |
| `prompts/ShortDescriptionPrompt.md` | Generic short description prompt |
| `prompts/ReviewYourChunks.md` | Chunk review prompt |

---

## 3 · Template Files (`templates/`)

XML/DITA templates used by `Convert.py` for document conversion.

| File | Purpose |
|------|---------|
| `templates/ct-concept.xml` | Concept topic template |
| `templates/ct-task.xml` | Task topic template |
| `templates/ct-reference.xml` | Reference topic template |
| `templates/ct-process.xml` | Process topic template |
| `templates/ct-principle.xml` | Principle topic template |
| `templates/chaptermap.ditamap` | DITA chapter map template |

---

## 4 · Config & Data Files (JSON)

| File | Read By | Purpose |
|------|---------|---------|
| `app_config.json` | `sidebar_app.py` | Persistent user preferences (product, tester name) |
| `product_keywords.json` | `sidebar_app.py` | Keyword rules for auto-detecting product from pasted content |
| `guide_mappings.json` | `app_functions.py` | Concept→guide mappings, install terms, noise words, stop words |
| `networking_terms.json` | `app_functions.py` | Networking technology term dictionary for guide matching |
| `data/heading_cache.json` | `app_functions.py` | Cached TOC headings per guide for chapter suggestions |
| `data/ingestion_metadata.json` | `incremental_ingestion.py` | Tracks file modification times for incremental updates |
| `inventory/sdwan/document_inventory.json` | `app_functions.py` | SD-WAN guide titles + source URLs for online links |

---

## 5 · Knowledge Docs (`knowledge_docs/`)

Source PDFs and Markdown files ingested into the ChromaDB vector store.
These are large (~387 MB) and are **.gitignored by default**. They must be
obtained separately and placed in the correct subdirectories.

```
knowledge_docs/
├── 9800/          # Cisco Catalyst 9800 guides
├── ASR9000/       # ASR 9000 guides
├── Cisco8000/     # Cisco 8000 guides
├── cisco_generic/ # Cross-product Cisco guides
├── iot/           # IoT guides
├── sdwan/         # SD-WAN guides
└── test/          # Test documents
```

---

## 6 · Environment & Infrastructure

| File | Purpose |
|------|---------|
| `.env` | **Required** — API keys (see below). Not committed to git. |
| `auth_token_cache.json` | Auto-generated Azure auth token cache. Git-ignored. |
| `requirements.txt` | Python package dependencies |
| `.gitignore` | Git ignore rules |
| `Denver.code-workspace` | VS Code workspace settings (optional) |

### Required `.env` Variables

```bash
# Choose one API type: "bridgeit" or "cxai"
CISCO_API_TYPE=bridgeit

# BridgeIt (Azure-backed)
BRIDGEIT_CLIENT_ID=...
BRIDGEIT_CLIENT_SECRET=...
BRIDGEIT_APP_KEY=...
BRIDGEIT_BRAIN_USER_ID=...

# — OR — CXAI (OpenAI-compatible)
OPENAI_API_BASE=...
OPENAI_API_KEY=...
```

---

## 7 · Documentation Files (optional, not needed to run)

These are developer docs and design notes. Include them for context but
they are not required at runtime.

| File | Purpose |
|------|---------|
| `README.md` | Project overview |
| `QUICKSTART.md` | Quick start guide |
| `FILE_GUIDE.md` | File guide |
| `AUTO_DETECT.md` | Product auto-detection design notes |
| `CHROMA_IN_MEMORY.md` | ChromaDB in-memory mode documentation |
| `GUIDE_MAPPING_PLAYBOOK.md` | Guide mapping rules documentation |
| `INCREMENTAL_INGESTION.md` | Incremental ingestion documentation |
| `MIGRATION_SUMMARY.md` | Migration summary |
| `bug_files.md` | Bug file format notes |
| `circuitapiuserguide.md` | Circuit API reference |

---

## 8 · Files You Do NOT Need

These are test scripts, one-off utilities, or generated artifacts:

| File | Reason |
|------|--------|
| `test_*.py` | Test scripts |
| `check_*.py` | One-off verification scripts |
| `fetch_bug.py` | Standalone bug fetch utility |
| `scour_books.py` | Book scouring utility |
| `merge_scour_concepts.py` | Scour merge utility |
| `downloadbooks_*.py` | Book download scripts |
| `extract_chapters.py` | Chapter extraction utility |
| `fix_sysintf_chapters.py` | One-off fix script |
| `quick_check_pages.py` | One-off page check |
| `basic_app.py` | Minimal test app |
| `scour_output/` | Generated scour output |
| `scour_output_sdwan/` | Generated scour output |
| `myenv/` | Virtual environment (recreate with `requirements.txt`) |
| `__pycache__/` | Python bytecode cache |
| `data/cisco_products_custom_loader/` | Legacy vector store location |

---

## 9 · Minimal File Checklist for a New Repository

Copy these files to create a working clone:

```
# Python source (core + pages)
sidebar_app.py
app_functions.py
utils.py
bug2.py
vector_store_manager.py
ingestion.py
start.py
sidebar_first_draft_page.py
sidebar_bulk_analysis_page.py
sidebar_resolve_bug_page.py
sidebar_hallucination_check_page.py

# Legacy tab app (optional — include if you want streamlit_app.py too)
streamlit_app.py
streamlit_app_sidebar_nav.py
first_draft_tab.py
bulk_analysis_tab.py
hal_check_tab.py
Convert.py

# CLI tools
debug_analysis.py
incremental_ingestion.py

# Prompt templates
BugAnalyze.md
summarize.md
SFSExplainer.md
InternalAnalysis.md
FirstDraftCTWG.md
HallucinationCheck.md
ChapterFinder.md
ContentWriter.md
ShortDescriptionPrompt.md
prompts/bookSD.md
prompts/chapterSD.md
prompts/H1SD.md
prompts/ShortDescriptionPrompt.md
prompts/ReviewYourChunks.md

# XML/DITA templates
templates/chaptermap.ditamap
templates/ct-concept.xml
templates/ct-task.xml
templates/ct-reference.xml
templates/ct-process.xml
templates/ct-principle.xml

# Config & data
app_config.json
product_keywords.json
guide_mappings.json
networking_terms.json
data/heading_cache.json
data/ingestion_metadata.json
inventory/sdwan/document_inventory.json

# Infrastructure
requirements.txt
.gitignore
.env                  # (create manually — never commit)

# Knowledge docs (obtain separately — too large for git)
knowledge_docs/       # place PDFs/MDs in product subdirectories

# Documentation (optional)
README.md
QUICKSTART.md
PROJECT_FILES.md
```
