# Onboarding ASR 9000 into Denver

Status tracker for bringing Cisco ASR 9000 Series Aggregation Services Routers documentation into the Denver pipeline.

---

## What's Already Done

| Step | Status | Notes |
|------|--------|-------|
| `knowledge_docs/ASR9000/` folder | ✅ | 32 legacy PDFs present (will be archived) |
| `config/product_keywords.json` | ✅ | ASR 9000 keywords registered |
| Product mappings (`sidebar_app.py`, `app_functions.py`) | ✅ | "ASR 9000" ↔ "ASR9000" wired up |
| Admin page registry (`sidebar_admin_page.py`) | ✅ | "ASR 9000" registered with release filter support |
| `admin/download_asr9000.py` | ✅ | Rewritten as HTML→Markdown pipeline (was PDF-only) |
| `ontology/ASR9000/guide_mappings.json` | ❌ | Needs creation |
| `inventory/ASR9000/document_inventory.json` | ❌ | Will be created by first download run |

---

## Phase 0 — Documentation Pipeline (HTML → Markdown)

### Landing Pages Scraped

The download script discovers books from two cisco.com support pages:
1. **Configuration guides**: `products-installation-and-configuration-guides-list.html`
2. **Install guides**: `products-installation-guides-list.html`

Plus manually curated extra URLs (IOS XR Smart Licensing guide).

### Skip Patterns

The following URL patterns are automatically excluded:
- `release/notes`, `release-notes` — release notes
- `/mcl` — end-of-life notices
- `/videos/` — video links
- `.zip` — archive downloads
- `.pdf` — direct PDF links (we want HTML chapters)
- `rcsi` — regulatory compliance docs

### Step 0a: Archive Existing PDFs

Move the 32 legacy PDFs out of `knowledge_docs/ASR9000/` before downloading HTML chapters:

```bash
python admin/download_asr9000.py --archive
```

Output: PDFs moved to `pdf_archive/ASR9000/`

### Step 0b: Build Inventory (Dry Run)

Discover books from the landing pages and list chapters without downloading:

```bash
# Dry run — discover books and list chapters, no download
python admin/download_asr9000.py --dry-run

# Filter to a specific release (e.g. latest 26xx)
python admin/download_asr9000.py --dry-run --release 26
```

Output: `inventory/ASR9000/document_inventory.json`

### Step 0c: Download HTML Chapters → Convert to Markdown

```bash
# Full pipeline: discover → download HTML → convert to Markdown
python admin/download_asr9000.py

# With release filter (recommended to avoid downloading all releases)
python admin/download_asr9000.py --release 26

# Download only one book
python admin/download_asr9000.py --book b-routing-cg-asr9000-26xx

# Re-download everything (overwrite existing)
python admin/download_asr9000.py --force

# Re-convert cached HTML to Markdown (no network)
python admin/download_asr9000.py --reconvert
```

Output:
- Raw HTML: `data/html_archive/ASR9000/<book>/<chapter>.html`
- Markdown:  `knowledge_docs/ASR9000/<book>/<chapter>.md`

### Step 0d: Validate Coverage

Check that every chapter in the inventory has a Markdown file:

```bash
python admin/download_asr9000.py --validate
```

### Step 0e: Compare PDFs vs Markdown

See which archived PDFs now have Markdown equivalents and which gaps remain:

```bash
python admin/download_asr9000.py --compare
```

### Step 0f: Rebuild Vector Store

After Markdown files are in place, go to Admin tab → **Rebuild Vector Store** (check the confirmation box). This re-ingests everything in `knowledge_docs/` into ChromaDB.

---

## Admin UI

The Admin page has ASR 9000 in the product dropdown with:
- **Release filter**: Enter a release (e.g. `26` for 26xx, or `25.1`) to download only that release. Leave blank for all releases.
- **Force refresh**: Re-download even if files already exist.
- **Start Download**: Runs the full pipeline (discover → inventory → download HTML → convert to Markdown).

---

## Phase 1 — Scour & Vocabulary

### Step 1a: Seed Product-Specific Vocabulary

Review `config/networking_terms.json`. Most protocol terms already exist. Add ASR 9000-specific feature phrases:

- IOS XR: `segment routing`, `srv6`, `traffic engineering`, `flexible algorithm`, `tilfa`, `evpn`, `l2vpn`, `l3vpn`, `bfd`, `netconf`, `grpc`, `telemetry`
- Carrier-grade: `bng`, `cgnat`, `carrier-grade nat`, `subscriber management`, `lawful intercept`
- Hardware: `line card`, `rsp`, `fabric card`, `optics`, `npu`, `satellite`, `nv cluster`

### Step 1b: Run scour_books.py

```bash
python scour_books.py --product ASR9000
```

Output lands in `scour_output/`.

---

## Phase 2 — Mappings & Tuning

Follow the generic playbook in [How to onboard a new product.md](How%20to%20onboard%20a%20new%20product.md), starting at **Phase 2, Step 4**:

1. **Review gap report** → `scour_output/gap_report_new_terms.json`
2. **Merge scoured mappings** → `ontology/ASR9000/guide_mappings.json` under `concept_to_guide`
3. **Identify reference guides** → add to `reference_guides.patterns`
4. **Remove noise terms** that match >60% of guides
5. **Check install/upgrade triggers** in `ontology/_shared/guide_mappings.json`

---

## Phase 3 — Test & Tune

1. Get 3–5 real ASR 9000 RCAs/bug reports
2. Add them as test cases in `debug_analysis.py`
3. Run `python debug_analysis.py --rca <name> --no-llm` and check the top-3 guide rankings
4. Tune if needed (see playbook for scoring constants)

---

## Remaining Checklist

- [ ] Run `--archive` to move 32 legacy PDFs
- [ ] Run `--dry-run` to verify book discovery
- [ ] Pick a target release (e.g. `--release 26`) to keep one version
- [ ] Run full download pipeline
- [ ] Run `--validate` to confirm coverage
- [ ] Run `--compare` to cross-check PDFs vs Markdown
- [ ] Rebuild vector store
- [ ] Create `ontology/ASR9000/guide_mappings.json`
- [ ] Seed ASR 9000 vocab terms
- [ ] Run `scour_books.py --product ASR9000`
- [ ] Review gap report & merge mappings
- [ ] Populate `concept_to_guide`
- [ ] Test with real RCAs
- [ ] Commit everything to git
