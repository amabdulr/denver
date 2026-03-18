# Knowledge Graph (kgraph) Pipeline

> Extract RDF triples from product documentation chapters using an AI prompt, producing a structured knowledge graph stored in JSON.

---

## Table of Contents

1. [Overview](#overview)
2. [Architecture](#architecture)
3. [Prerequisites](#prerequisites)
4. [File Inventory](#file-inventory)
5. [Running the Pipeline](#running-the-pipeline)
6. [How It Works](#how-it-works)
7. [The kgraph.md Prompt](#the-kgraphmd-prompt)
8. [Output Format](#output-format)
9. [Monitoring a Run](#monitoring-a-run)
10. [Resume & Crash Safety](#resume--crash-safety)
11. [Troubleshooting](#troubleshooting)
12. [Adding a New Product](#adding-a-new-product)
13. [Reference: SD-WAN Baseline Run](#reference-sd-wan-baseline-run)

---

## Overview

The kgraph pipeline reads every chapter of every book in a product's document inventory, sends the chapter content to an LLM with a structured prompt (`kgraph.md`), and parses the response into pipe-delimited RDF triples. These triples form a per-product knowledge graph used for entity linking, search enrichment, and documentation analysis.

```
Document Inventory  ──►  Chapter Text Cache  ──►  LLM (kgraph.md prompt)  ──►  RDF Triples (JSON)
   (inventory/)         (knowledge_docs/)           (Claude Sonnet 4)        (config/ontology/)
```

---

## Architecture

```
scripts/gen_book_descriptions.py
    │
    ├── Reads:   inventory/<product>/document_inventory.json
    ├── Reads:   prompts/kgraph.md                          (AI prompt template)
    ├── Reads:   knowledge_docs/<product>/<book>/<chapter>.md   (cached text)
    │
    ├── Calls:   LLM via app/utils.py  →  BridgeIt API (Claude Sonnet 4)
    │
    └── Writes:  config/ontology/<product>/book_kgraph.json     (output)
```

### Key Constants (in the script)

| Constant | Value | Purpose |
|---|---|---|
| `MAX_CONTENT_CHARS` | 50,000 | Max chars of chapter text sent to LLM |
| `MIN_USABLE_CHARS` | 200 | Text shorter than this is skipped |
| `MAX_RETRIES` | 4 | LLM retry attempts per chapter |
| `LLM_TIMEOUT` | 90s | Max wait per LLM invocation |
| `DEFAULT_MODEL` | `claude-sonnet-4` | LLM model |

---

## Prerequisites

1. **Python venv** activated: `source .venv/bin/activate`
2. **BridgeIt credentials** configured in `.env` (JWT auth, auto-refreshes)
3. **Document inventory** exists: `inventory/<product>/document_inventory.json`
4. **Chapter text cached** in `knowledge_docs/<product>/` — the pipeline can fetch HTML if missing, but pre-cached `.md` files are strongly preferred (see the HTML download scripts in `admin/`)

---

## File Inventory

| File | Purpose |
|---|---|
| `scripts/gen_book_descriptions.py` | Main pipeline script |
| `prompts/kgraph.md` | AI prompt defining triple extraction rules, predicate whitelist, category types, and self-audit checks |
| `inventory/<product>/document_inventory.json` | List of books → chapters → URLs |
| `knowledge_docs/<product>/<book-slug>/<chapter-slug>.md` | Cached chapter text (markdown) |
| `config/ontology/<product>/book_kgraph.json` | Output — all extracted triples |

---

## Running the Pipeline

### Full run (all chapters for a product)

```bash
cd Denver2
python -u scripts/gen_book_descriptions.py 2>&1 | tee /tmp/kgraph_run.log
```

### Single book

```bash
python -u scripts/gen_book_descriptions.py --book routing-book-xe.pdf
```

### Different product

```bash
python -u scripts/gen_book_descriptions.py --product Cisco8000
```

### Dry run (list what would be processed, no LLM calls)

```bash
python scripts/gen_book_descriptions.py --dry-run
```

### Fetch-only (download chapter text, no LLM calls)

```bash
python scripts/gen_book_descriptions.py --fetch-only
```

### Background run with log

```bash
rm -f data/auth_token_cache.json   # force fresh token
python -u scripts/gen_book_descriptions.py 2>&1 | tee /tmp/kgraph_run.log &
```

---

## How It Works

### Step-by-step per chapter:

1. **Check cache** — Look for `knowledge_docs/<product>/<book-slug>/<chapter-slug>.md` (preferred) or `.pdf` (fallback)
2. **Fetch HTML** — If no cache exists and a URL is available, fetch the chapter HTML page, extract text with BeautifulSoup, and cache it as `.md`
3. **Validate** — Skip if text < 200 chars
4. **Call LLM** — Send the full kgraph.md prompt + chapter context to Claude Sonnet 4
5. **Parse triples** — Extract pipe-delimited lines with 5 columns: `Subject|Predicate|Object|CategoryType|SourceTrace`
6. **Save** — Write the entire JSON output after every chapter (crash-safe)

### Token auto-refresh

The BridgeIt JWT token expires after ~1 hour. The script detects 401 errors and automatically refreshes the token by invalidating the cache and re-calling `get_llm()`.

### Rate limiting

- 1 second delay between LLM calls (`LLM_DELAY`)
- 0.5 second delay between HTML fetches (`FETCH_DELAY`)
- If a 429 (Spike Arrest) error is returned, the script retries after a backoff

---

## The kgraph.md Prompt

The prompt at `prompts/kgraph.md` (~745 lines, ~39K chars) defines:

- **Predicate whitelist** — ~33 approved predicates (e.g., `isA`, `isPartOf`, `configuredVia`, `requires`, `mitigates`)
- **CategoryType taxonomy** — ~25 types (e.g., `Feature`, `Platform`, `Protocol`, `CLI-Command`, `Troubleshooting`)
- **Section 2A** — Feature-relationship extraction rules
- **Section 2B** — Task-intent triples (action verbs → step sequences)
- **Section 2C** — Troubleshooting triples (symptom → cause → resolution)
- **Section 2D** — Concept linking across documentation boundaries
- **Section 2E** — Graph connectivity rule (no orphan entities)
- **Self-audit checklist** — 10 checks the LLM runs before emitting output

### Key rule: No Orphan Entities (Section 2E)

Every entity that appears as a Subject must also appear in at least one other triple (as Subject or Object). This ensures a fully connected graph with no isolated nodes.

---

## Output Format

The output file `config/ontology/<product>/book_kgraph.json` has this structure:

```json
{
  "appqoe-book-xe.pdf": {
    "title": "Cisco Catalyst SD-WAN AppQoE Configuration Guide...",
    "chapters": {
      "m-appnav-xe-for-sd-wan": {
        "title": "AppNav-XE for Cisco Catalyst SD-WAN",
        "url": "https://...",
        "source": "cache",
        "triples": [
          "AppNav-XE|isA|Feature|Feature|m-appnav-xe-for-sd-wan.md",
          "AppNav-XE|isPartOf|AppQoE|Feature|m-appnav-xe-for-sd-wan.md",
          "AppNav-XE|requires|Service Controller|Component|m-appnav-xe-for-sd-wan.md"
        ]
      }
    }
  }
}
```

Each triple follows the format:

```
Subject|Predicate|Object|CategoryType|SourceTrace
```

---

## Monitoring a Run

### Watch the log in real time

```bash
tail -f /tmp/kgraph_run.log
```

### Check progress from the JSON

```bash
cd Denver2
python3 -c "
import json
r = json.load(open('config/ontology/sdwan/book_kgraph.json'))
done = sum(1 for b in r.values() if isinstance(b,dict)
           for c in b.get('chapters',{}).values() if 'triples' in c)
triples = sum(len(c.get('triples',[])) for b in r.values()
              if isinstance(b,dict) for c in b.get('chapters',{}).values())
print(f'Chapters done: {done}/367  |  Triples: {triples}')
"
```

### Check if the process is alive

```bash
ps aux | grep gen_book_descriptions | grep -v grep
```

---

## Resume & Crash Safety

The pipeline saves the full JSON after every chapter. If it crashes or is killed:

- **Already-processed chapters are skipped** — the script checks for the `triples` key in each chapter entry
- **Just re-run the same command** — it picks up where it left off
- **No duplicates** — each chapter is a dict key; re-processing replaces (not appends)

### To force re-processing of all chapters

Clear the triples from the JSON:

```bash
python3 -c "
import json
data = json.load(open('config/ontology/sdwan/book_kgraph.json'))
for book in data.values():
    if isinstance(book, dict) and 'chapters' in book:
        for ch in book['chapters'].values():
            ch.pop('triples', None)
            ch.pop('source', None)
json.dump(data, open('config/ontology/sdwan/book_kgraph.json', 'w'), indent=2)
print('Cleared all triples')
"
```

Then re-run the pipeline.

---

## Troubleshooting

| Problem | Cause | Fix |
|---|---|---|
| `Auth token expired` warning | BridgeIt JWT expired (1h TTL) | Auto-handled. If persistent, delete `data/auth_token_cache.json` and rerun |
| `429 Spike Arrest` | API rate limit | Auto-retried with backoff. Reduce concurrent usage if frequent |
| `Connection error` (all 4 retries fail) | Network issue / API outage | Chapter gets 0 triples. Re-run later to fill gaps |
| `0 triples` for a chapter | Short content, LLM timeout, or connection failures | Check the source content length. Re-run with triples cleared for that chapter |
| `text too short (N chars)` | Chapter cache has minimal content | Re-download the HTML: delete the `.md` cache file and re-run with `--fetch-only` |
| Pipeline stuck / no log output | LLM call hanging beyond timeout | Check `ps aux` — if alive, wait. If the log hasn't moved in 15+ min, kill and restart (resume is automatic) |
| Output JSON missing | Directory deleted (e.g., OneDrive sync) | Recreate directory: `mkdir -p config/ontology/<product>` and restart |

---

## Adding a New Product

1. **Create the document inventory** at `inventory/<product>/document_inventory.json` (see existing sdwan inventory for format)
2. **Download chapter text** into `knowledge_docs/<product>/` using the admin download scripts or `--fetch-only` mode
3. **Run the pipeline**:
   ```bash
   python -u scripts/gen_book_descriptions.py --product <product> 2>&1 | tee /tmp/kgraph_<product>.log
   ```
4. **Output** appears at `config/ontology/<product>/book_kgraph.json`

---

## Reference: SD-WAN Baseline Run

The production SD-WAN knowledge graph was generated on **17–18 March 2026** with these parameters:

| Metric | Value |
|---|---|
| Books | 28 |
| Chapters | 367 |
| Total triples | 13,527 |
| Chapters with 0 triples | 11 |
| Avg triples per chapter | 36.9 |
| Model | Claude Sonnet 4 |
| Prompt | kgraph.md (745 lines, ~39K chars) |
| Source | `.md` cached files (full content, up to 50K chars) |
| Avg time per chapter | ~51s |
| Total runtime | ~3 hours (across resume runs) |
| Output | `config/ontology/sdwan/book_kgraph.json` (2.5 MB) |
