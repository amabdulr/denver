# 📁 Denver Project — File & Folder Guide

> **Bug Doctor** — A Streamlit-based assistant for analyzing Cisco bugs/RCAs, mapping them to documentation guides, generating first drafts, and checking for hallucinations. Built on RAG (Retrieval-Augmented Generation) with ChromaDB and LangChain.

---

## 🌐 Streamlit Web App

| File | Description |
|------|-------------|
| `sidebar_app.py` | **Main entry point.** Sidebar-nav Streamlit app ("Bug Doctor") tying together all pages — product/model selection, persistent config, and page routing. |
| `streamlit_app.py` | Original tab-based Streamlit app (predecessor to `sidebar_app.py`) with Analysis, First Draft, Convert, Bulk Analysis, and Hallucination Check tabs. |
| `streamlit_app_sidebar_nav.py` | Proof-of-concept demo comparing sidebar navigation vs. tab-based navigation in Streamlit. |
| `start.py` | Unified startup script — pre-initializes the in-memory ChromaDB vector store (for old SQLite compatibility), then launches `sidebar_app.py`. |
| `basic_app.py` | Minimal "Hello World" Streamlit demo app used for initial testing. |

### Sidebar Pages

| File | Description |
|------|-------------|
| `sidebar_bulk_analysis_page.py` | Bulk Analysis page — processes multiple RCAs or bugs from an uploaded Excel file, with guide selection, progress tracking, pause/resume, and Excel export. |
| `sidebar_first_draft_page.py` | First Draft page — two-step workflow (identify internal info → generate customer-facing draft) with multi-file upload support (.txt, .md, .doc, .docx, .pdf). |
| `sidebar_hallucination_check_page.py` | Hallucination Check page — compares original source docs with AI-generated content to flag fabrications, with file upload and follow-up questions. |
| `sidebar_resolve_bug_page.py` | Resolve Bug page — fetches CDETS bug metadata, generates AI-assisted resolution comments, posts R-comments back to CDETS, and sends resolution emails. |

### Tab Components (used by `streamlit_app.py`)

| File | Description |
|------|-------------|
| `bulk_analysis_tab.py` | Bulk analysis tab — processes multiple RCAs from Excel through ChapterFinder and ContentWriter workflows. |
| `first_draft_tab.py` | First Draft tab — explains SFS content, finds internal/confidential info, and generates a customer-facing first draft. |
| `hal_check_tab.py` | Hallucination Check tab — pastes original + AI-generated content and uses an LLM to identify inaccuracies. |
| `Convert.py` | Convert tab — transforms raw content into structured DITA XML (concept, task, reference, etc.) using AI and XML templates. |

---

## 🧠 Core Engine & Utilities

| File | Description |
|------|-------------|
| `app_functions.py` | **Core business logic.** RAG vector DB queries (Chroma + HuggingFace), LangChain agent orchestration, LLM calls, output formatting, and prompt template loading. |
| `utils.py` | Shared utilities — environment validation, Azure/BridgeIT OAuth token retrieval with local caching, and LLM instantiation supporting BridgeIT and CXAI endpoints. |
| `vector_store_manager.py` | Singleton ChromaDB manager — auto-detects SQLite version to choose persistent vs. in-memory mode, handles OneDrive→local migration, and provides global accessors. |
| `bug2.py` | CDETS (Cisco Defect Tracking System) API client — OAuth1 auth, bug fetching, notes/files retrieval, comment posting, and safe XML/HTML parsing. |

---

## 📥 Document Ingestion & Knowledge Base

| File | Description |
|------|-------------|
| `ingestion.py` | Core ingestion module — loads PDFs/text files, builds page-to-section maps, splits into chunks with rich metadata (page numbers, sections), and stores embeddings in ChromaDB. |
| `incremental_ingestion.py` | Smart incremental ingestion — tracks file metadata (timestamps, sizes) in JSON and only processes new/modified docs, skipping unchanged files and removing stale embeddings. |
| `downloadbooks_landing.py` | Web scraper for the Cisco SD-WAN support page — filters by release version and downloads PDF guides in parallel for ingestion. |
| `downloadbooks_iot_collection.py` | Web scraper for a Cisco IoT documentation collection — crawls subpages for PDF links and downloads them in parallel. |
| `scour_books.py` | PDF analysis pipeline — extracts TOC headings from PDFs, sends them to an LLM for concept/synonym extraction, and cross-references against the networking terms vocabulary to build concept-to-guide mappings. |
| `merge_scour_concepts.py` | Post-processing script — merges concept-to-guide mappings from `scour_books.py` into `networking_terms.json` and `guide_mappings.json`, with noise filtering. |
| `extract_chapters.py` | Enrichment script — reads `guide_mappings.json`, scrapes Cisco.com book landing pages to extract chapter names/slugs/URLs, and writes the enriched data back. |
| `fix_sysintf_chapters.py` | One-off fix script to extract and update chapter data for a specific guide in `guide_mappings.json`. |

---

## 🔍 Bug Fetching & Analysis

| File | Description |
|------|-------------|
| `fetch_bug.py` | Simple CLI script — fetches and prints key fields (Headline, Status, Severity, etc.) and the first few notes of a specific CDETS bug. |
| `debug_analysis.py` | CLI debug tool — replicates the Analysis tab workflow without Streamlit, allowing step-by-step tracing of RAG retrieval, term matching, and LLM prompt assembly against test RCAs. |
| `check_bug_fields.py` | Diagnostic — fetches a CDETS bug and lists all available field names/values, with optional highlighting of specific fields. |

---

## 🧪 Test & Diagnostic Scripts

| File | Description |
|------|-------------|
| `test_setup.py` | Integration tests verifying the full in-memory ChromaDB pipeline: doc loading, vector store init, access, and query. |
| `test_all_models.py` | Validates multiple LLM models against the full Analysis & Summary workflow (including RAG retrieval). |
| `test_models.py` | Model identity check — sends each model a "tell me your name" prompt to confirm endpoints route to distinct models. |
| `check_models.py` | Discovery script — iterates through LLM model names via the BridgeIT API to see which are available and working. |
| `test_component_field.py` | Verifies fetching specific CDETS bug fields (Component, To-be-fixed, Status) via the API. |
| `test_email.py` | Tests the bug resolution email flow through various Cisco SMTP servers. |
| `test_post_resolution.py` | Tests posting an R-comment (resolution comment) to a CDETS bug. |
| `test_r_comment.py` | Tests posting R-comments to CDETS with CLI arg support for specifying the bug number. |
| `check_html_files.py` | Samples documents from ChromaDB to check for erroneously ingested HTML files. |
| `check_page_numbers.py` | Queries the vector store to verify PDF page number metadata is preserved in embeddings. |
| `quick_check_pages.py` | Lightweight diagnostic — connects directly to ChromaDB (no embeddings model) to quickly check page number metadata. |

---

## 📝 LLM Prompt Templates

### Root-Level Prompts (loaded by `app_functions.py`)

| File | Description |
|------|-------------|
| `BugAnalyze.md` | System prompt for analyzing a bug/RCA to determine which product guide chapters are best for new documentation. |
| `ContentWriter.md` | System prompt for generating ready-to-use user-guide content (steps, caveats, workarounds) from a completed analysis. |
| `ChapterFinder.md` | System prompt for searching the vector store for pinned guide recommendations and writing doc content for a bug/RCA. |
| `FirstDraftCTWG.md` | System prompt for transforming an internal SFS into a customer-facing user guide, filtering out confidential details. |
| `SFSExplainer.md` | System prompt for explaining an SFS to a technical writer — summarizes user-facing features with analogies. |
| `InternalAnalysis.md` | System prompt for reviewing an SFS and identifying internal/implementation details that shouldn't be customer-facing. |
| `HallucinationCheck.md` | System prompt for comparing original source content against AI output to detect fabricated claims and hallucinations. |
| `ShortDescriptionPrompt.md` | Rules and examples for generating short descriptions per information type (Task, Concept, Process, Reference, etc.). |
| `summarize.md` | Prompt template instructing an LLM to extract and summarize bug report details into structured JSON. |

### `prompts/` Directory

| File | Description |
|------|-------------|
| `bookSD.md` | Prompt template for generating short descriptions of entire books/guides. |
| `chapterSD.md` | Prompt template for generating short descriptions of chapters. |
| `H1SD.md` | Prompt template for generating short descriptions of H1 (heading-level-1) sections. |
| `ReviewYourChunks.md` | Comprehensive prompt for evaluating documentation chunks against info-type rules and rewriting if needed. |
| `ShortDescriptionPrompt.md` | Same as root-level `ShortDescriptionPrompt.md` — rules for writing short descriptions by information type. |

---

## ⚙️ Configuration & Data Files

| File | Description |
|------|-------------|
| `app_config.json` | Runtime settings — stores the selected product name and tester name. |
| `guide_mappings.json` | Maps detected networking terms to PDF guide filenames per product, including reference guides, scoring rules, and chapter metadata. |
| `networking_terms.json` | Extensive list of networking feature terms (e.g., "10 gigabit ethernet", "BGP") used by the pre-extraction engine for keyword matching in bug/RCA content. |
| `product_keywords.json` | Maps product names (SD-WAN, ASR 9000, Cisco 8000, etc.) to keyword lists for auto-detecting which product a pasted bug/RCA belongs to. |
| `auth_token_cache.json` | Cached Azure/BridgeIT OAuth tokens to avoid repeated auth requests. |
| `requirements.txt` | Python package dependencies for the project. |
| `Denver.code-workspace` | VS Code workspace configuration file. |

---

## 📂 Folders

| Folder | Description |
|--------|-------------|
| `knowledge_docs/` | Source PDF and text documents organized by product (`9800/`, `ASR9000/`, `Cisco8000/`, `iot/`, `sdwan/`, `cisco_generic/`, `test/`) — the raw knowledge base that gets ingested into ChromaDB. |
| `data/` | Runtime data — contains the ChromaDB SQLite databases (`cisco_products_custom_loader/`), heading caches (`heading_cache.json`), and ingestion metadata (`ingestion_metadata.json`). |
| `prompts/` | LLM prompt templates for generating short descriptions and reviewing documentation chunks (see table above). |
| `templates/` | DITA XML templates (`ct-concept.xml`, `ct-task.xml`, `ct-reference.xml`, `ct-principle.xml`, `ct-process.xml`, `chaptermap.ditamap`) used by the Convert tab to structure AI-generated content. |
| `scour_output/` | Output from `scour_books.py` runs on default/SD-WAN guides — contains `draft_concept_mappings.json`, `gap_report_new_terms.json`, `raw_results.json`, and `summary.txt`. |
| `scour_output_sdwan/` | Same as `scour_output/` but specifically for SD-WAN product guides. |
| `myenv/` | Python virtual environment (venv) for the project. |
| `__pycache__/` | Python bytecode cache (auto-generated). |
| `test/` | Test-related files and data. |

---

## 📖 Documentation & Guides

| File | Description |
|------|-------------|
| `README.md` | Main project README — describes features, setup, and usage. |
| `QUICKSTART.md` | Quick-start guide for running the app under in-memory ChromaDB mode. |
| `GUIDE_MAPPING_PLAYBOOK.md` | Step-by-step playbook for onboarding a new Cisco product — scouring PDFs, building guide mappings, wiring keywords, and testing scoring. |
| `AUTO_DETECT.md` | Documents auto-detection of SQLite version and ChromaDB mode selection. |
| `CHROMA_IN_MEMORY.md` | Explains the in-memory ChromaDB workaround for servers with old SQLite (<3.35). |
| `INCREMENTAL_INGESTION.md` | Documents the incremental ingestion feature for processing only new/modified PDFs. |
| `MIGRATION_SUMMARY.md` | Changelog for the persistent → in-memory ChromaDB migration, with file-level diffs. |
| `bug_files.md` | Sample bug report dump (CSCwr82677) used as test data. |
| `circuitapiuserguide.md` | Example Python code for calling the Cisco CircuIT (Bridge) chat API. |
