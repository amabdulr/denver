# Onboarding Cisco 8000 into Denver

Status tracker for bringing Cisco 8000 Series Routers documentation into the Denver pipeline.

---

## What's Already Done

| Step | Status | Notes |
|------|--------|-------|
| `knowledge_docs/Cisco8000/` folder | ✅ | 31 PDFs already present |
| `config/product_keywords.json` | ✅ | Cisco 8000 keywords registered |
| Product mappings (`sidebar_app.py`, `app_functions.py`) | ✅ | "Cisco 8000" ↔ "Cisco8000" wired up |
| Admin page registry (`sidebar_admin_page.py`) | ✅ | "Cisco 8000" registered in `PRODUCT_DOWNLOAD_REGISTRY` |
| `ontology/Cisco8000/guide_mappings.json` | ⚠️ | File exists, `product_noise` populated, but `concept_to_guide` is empty |

---

## Phase 0 — Documentation Pipeline (HTML → Markdown)

### Important: Always Specify a Release

Cisco publishes the same configuration guide for every IOS XR release (e.g. 24xx, 25xx, 26xx, 710x, 711x). **If you omit the release filter, you will download all of them** — the same content repeated 7+ times. Always pick one release:

| Release | IOS XR Branch | Notes |
|---------|---------------|-------|
| `26`    | 26xx (IOS XR 7.x LTS) | Recommended — latest classic branch, most chapters |
| `711`   | 711x (IOS XR 24.x) | Latest innovation branch |

Release-independent books (hardware install guides, migration guides, licensing) are **always included** regardless of the filter.

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

Move legacy PDFs out of `knowledge_docs/Cisco8000/` before downloading HTML chapters:

```bash
python admin/download_cisco8000.py --archive
```

Output: PDFs moved to `pdf_archive/Cisco8000/`

### Step 0b: Build Inventory (Dry Run)

Discover books and list chapters without downloading:

```bash
# Dry run with release filter (recommended)
python admin/download_cisco8000.py --dry-run --release 26

# Dry run without filter (shows ALL releases — use to audit)
python admin/download_cisco8000.py --dry-run
```

Output: `inventory/Cisco8000/document_inventory.json`

### Step 0c: Download HTML Chapters → Convert to Markdown

```bash
# Full pipeline with release filter (recommended)
python admin/download_cisco8000.py --release 26

# Download only one book
python admin/download_cisco8000.py --book b-segment-routing-cg-cisco8000-26xx

# Re-download everything (overwrite existing)
python admin/download_cisco8000.py --release 26 --force

# Re-convert cached HTML to Markdown (no network)
python admin/download_cisco8000.py --reconvert
```

Output:
- Raw HTML: `data/html_archive/Cisco8000/<book>/<chapter>.html`
- Markdown:  `knowledge_docs/Cisco8000/<book>/<chapter>.md`

### Step 0d: Validate Coverage

Check that every chapter in the inventory has a Markdown file:

```bash
python admin/download_cisco8000.py --validate
```

### Step 0e: Compare PDFs vs Markdown

See which archived PDFs now have Markdown equivalents and which gaps remain:

```bash
python admin/download_cisco8000.py --compare
```

Reports:
- **Matched**: PDFs that have a corresponding Markdown book folder (with chapter counts)
- **PDF-only**: Archived PDFs with no Markdown download yet (gaps to fill)
- **Markdown-only**: Books downloaded via HTML that had no prior PDF

### Step 0f: Rebuild Vector Store

After Markdown files are in place, go to Admin tab → **Rebuild Vector Store** (check the confirmation box). This re-ingests everything in `knowledge_docs/` into ChromaDB.

---

## Admin UI

The Admin page has Cisco 8000 in the product dropdown with:
- **Release filter**: Enter a release (e.g. `26` for 26xx) to download only that release. Leave blank for all releases (not recommended). Release-independent books (hardware install guides, licensing, migration) are always included.
- **Force refresh**: Re-download even if files already exist.
- **Start Download**: Runs the full pipeline (discover → inventory → download HTML → convert to Markdown).

---

## Phase 1 — Scour & Vocabulary

### Step 1a: Seed Product-Specific Vocabulary

Review `config/networking_terms.json`. Most protocol terms (BGP, OSPF, MPLS, etc.) already exist. Add Cisco 8000-specific feature phrases to the `features` array:

- IOS XR-specific: `segment routing`, `srv6`, `traffic engineering`, `flexible algorithm`, `tilfa`, `evpn`, `l2vpn`, `l3vpn`, `bfd`, `netconf`, `grpc`, `telemetry`
- Hardware-specific: `line card`, `fabric`, `optics`, `breakout`, `npu`, `memory utilization`
- Check what terms appear in the existing 31 PDFs to guide additions

### Step 1b: Run scour_books.py

```bash
python scour_books.py --product Cisco8000
# Takes 20-40 min. Use --resume if it crashes.
```

Output lands in `scour_output/`.

---

## Phase 2 — Mappings & Tuning

Follow the generic playbook in [How to onboard a new product.md](How%20to%20onboard%20a%20new%20product.md), starting at **Phase 2, Step 4**:

1. **Review gap report** → `scour_output/gap_report_new_terms.json`
2. **Merge scoured mappings** → `ontology/Cisco8000/guide_mappings.json` under `concept_to_guide`
3. **Identify phone-book/reference guides** → add to `reference_guides.patterns`
4. **Remove noise terms** that match >60% of guides
5. **Check install/upgrade triggers** in `ontology/_shared/guide_mappings.json`

---

## Phase 3 — Test & Tune

1. Get 3–5 real Cisco 8000 RCAs/bug reports
2. Add them as test cases in `debug_analysis.py`
3. Run `python debug_analysis.py --rca <name> --no-llm` and check the top-3 guide rankings
4. Tune if needed (see playbook for scoring constants)

---

## Remaining Checklist

- [ ] Run `--archive` to move legacy PDFs
- [ ] Run `--dry-run --release 26` to verify book discovery
- [ ] Run full download with `--release 26`
- [ ] Run `--validate` to confirm coverage
- [ ] Run `--compare` to cross-check PDFs vs Markdown
- [ ] Rebuild vector store
- [ ] Seed Cisco 8000 vocab terms
- [ ] Run `scour_books.py --product Cisco8000`
- [ ] Review gap report & merge mappings
- [ ] Populate `concept_to_guide` in `ontology/Cisco8000/guide_mappings.json`
- [ ] Identify reference/phone-book guides
- [ ] Test with real RCAs
- [ ] Commit everything to git
