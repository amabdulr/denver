"""
Admin Page — sidebar page for administrative tasks.

Three sections:
  1. Inventory Manager   — create / review / edit document inventories
  2. Download Documentation — download + convert from saved inventory
  3. Rebuild Vector Store  — re-ingest knowledge_docs/ into ChromaDB
"""

import importlib
import inspect
import json
import os
import shutil
import sys
from typing import Optional

import streamlit as st
from paths import PROJECT_ROOT, KNOWLEDGE_DOCS_DIR, CONFIG_DIR, INVENTORY_DIR

# Ensure admin.* imports resolve
if PROJECT_ROOT not in sys.path:
    sys.path.insert(0, PROJECT_ROOT)

from admin.inventory_manager import (
    PRODUCT_CONFIGS as INV_PRODUCTS,
    load_inventory,
    save_inventory,
    remove_books,
    inventory_stats,
    inventory_path,
    scrape_inventory,
    download_from_inventory,
)

# ---------------------------------------------------------------------------
# Products that do NOT use an inventory (legacy / simple downloaders).
# These only appear in the Download section.
# ---------------------------------------------------------------------------
LEGACY_DOWNLOAD_REGISTRY = {
    "Cisco SD-WAN (PDFs)": {
        "module": "admin.download_sdwan",
        "folder": os.path.join(KNOWLEDGE_DOCS_DIR, "sdwan"),
        "supports_release_filter": True,
        "release_placeholder": "e.g. 20.15",
    },
    "IoT": {
        "module": "admin.download_iot",
        "folder": os.path.join(KNOWLEDGE_DOCS_DIR, "iot"),
        "supports_release_filter": False,
        "release_placeholder": "",
    },
}


# ═══════════════════════════════════════════════════════════════════════
# render_admin_page
# ═══════════════════════════════════════════════════════════════════════

def render_admin_page():
    """Render the Admin page inside the main content area."""
    st.header("🛠️ Admin")
    st.markdown("Administrative tools for managing the knowledge base.")
    st.markdown("---")

    _render_inventory_manager()
    st.markdown("---")
    _render_download_section()
    st.markdown("---")
    _render_rebuild_vector_store()


# ═══════════════════════════════════════════════════════════════════════
# Section 1 — Inventory Manager
# ═══════════════════════════════════════════════════════════════════════

def _render_inventory_manager():
    st.subheader("📋 Inventory Manager")
    st.caption(
        "Create, review, and edit the document inventory for a product. "
        "The inventory lists every book and chapter that will be downloaded."
    )

    product_names = list(INV_PRODUCTS.keys())
    selected = st.selectbox("Product", product_names, key="inv_product")
    cfg = INV_PRODUCTS[selected]

    # ── Stats ──────────────────────────────────────────────────────────
    books, chapters = inventory_stats(selected)
    inv_file = inventory_path(selected)

    if books:
        st.info(f"📚 **{books}** books, **{chapters}** chapters  —  `{inv_file}`")
    else:
        st.warning("No inventory file found. Use **Scrape & Build** to create one.")

    # ── Scrape & Build ─────────────────────────────────────────────────
    if cfg["has_scraper"]:
        with st.expander("🔍 Scrape & Build Inventory", expanded=not books):
            if cfg["supports_release"]:
                release = st.text_input(
                    "Target Release (leave blank for all)",
                    placeholder=cfg["release_placeholder"],
                    key="inv_scrape_release",
                )
            else:
                release = ""

            if st.button("🚀 Scrape URLs", type="primary", key="inv_scrape_btn"):
                lines: list[str] = []
                log_area = st.empty()

                def _log(msg):
                    lines.append(str(msg))

                with st.spinner(f"Scraping {selected} book listings…"):
                    try:
                        inv = scrape_inventory(
                            selected,
                            target_release=release.strip() or None,
                            log=_log,
                        )
                        b = len(inv)
                        c = sum(len(v.get("chapters", [])) for v in inv.values())
                        _log(f"\n✅ Inventory saved — {b} books, {c} chapters")
                        log_area.code("\n".join(lines), language="text")
                        st.success(f"✅ Inventory built — {b} books, {c} chapters")
                        st.rerun()
                    except Exception as exc:
                        _log(f"\n❌ Error: {exc}")
                        log_area.code("\n".join(lines), language="text")
                        st.error(f"Scrape failed: {exc}")

    # ── Book list with remove ──────────────────────────────────────────
    if books:
        with st.expander("📖 Review Books", expanded=False):
            inv_data = load_inventory(selected)
            # Build a list for display
            rows = []
            for key, val in inv_data.items():
                ch_count = len(val.get("chapters", []))
                rows.append({
                    "key": key,
                    "title": val.get("title", key),
                    "chapters": ch_count,
                })

            # Multiselect for removal
            book_labels = [f"{r['title']}  ({r['chapters']} ch)" for r in rows]
            book_keys = [r["key"] for r in rows]

            to_remove = st.multiselect(
                "Select books to remove",
                options=book_keys,
                format_func=lambda k: next(
                    (f"{r['title']}  ({r['chapters']} ch)" for r in rows if r["key"] == k),
                    k,
                ),
                key="inv_remove_select",
            )

            if to_remove:
                if st.button(
                    f"🗑️ Remove {len(to_remove)} book(s)",
                    key="inv_remove_btn",
                ):
                    remove_books(selected, to_remove)
                    st.success(f"Removed {len(to_remove)} book(s)")
                    st.rerun()

        # ── Raw JSON editor ────────────────────────────────────────────
        with st.expander("✏️ Edit Raw JSON", expanded=False):
            inv_data = load_inventory(selected)
            edited_json = st.text_area(
                "Inventory JSON",
                value=json.dumps(inv_data, indent=2),
                height=400,
                key="inv_json_editor",
            )
            if st.button("💾 Save JSON", key="inv_json_save_btn"):
                try:
                    parsed = json.loads(edited_json)
                    save_inventory(selected, parsed)
                    st.success("✅ Inventory saved")
                    st.rerun()
                except json.JSONDecodeError as exc:
                    st.error(f"Invalid JSON: {exc}")


# ═══════════════════════════════════════════════════════════════════════
# Section 2 — Download Documentation
# ═══════════════════════════════════════════════════════════════════════

def _render_download_section():
    st.subheader("📥 Download Documentation")
    st.caption(
        "Download and convert documentation from cisco.com. "
        "Inventory-based products use the saved inventory (edit it above). "
        "Legacy products download directly."
    )

    # Combine inventory products + legacy products into one selector
    all_products: list[str] = list(INV_PRODUCTS.keys()) + list(LEGACY_DOWNLOAD_REGISTRY.keys())
    selected = st.selectbox("Product", all_products, key="dl_product")

    is_inventory_product = selected in INV_PRODUCTS

    # ── Release filter for legacy products ─────────────────────────────
    target_release = ""
    if not is_inventory_product:
        entry = LEGACY_DOWNLOAD_REGISTRY[selected]
        if entry["supports_release_filter"]:
            target_release = st.text_input(
                "Target Release (leave blank for all)",
                placeholder=entry["release_placeholder"],
                key="dl_release",
            )

    # ── Folder stats ───────────────────────────────────────────────────
    if is_inventory_product:
        cfg = INV_PRODUCTS[selected]
        folder = os.path.join(KNOWLEDGE_DOCS_DIR, cfg["inv_dir"])
    else:
        folder = LEGACY_DOWNLOAD_REGISTRY[selected]["folder"]

    st.caption(f"📂 Output folder: `{folder}`")
    _show_folder_stats(folder)

    # ── Inventory stats for inventory products ─────────────────────────
    if is_inventory_product:
        b, c = inventory_stats(selected)
        if b:
            st.caption(f"📋 Inventory: {b} books, {c} chapters")
        else:
            st.warning("No inventory found — go to **Inventory Manager** above to create one first.")

    # ── Force refresh checkbox ─────────────────────────────────────────
    force_refresh = st.checkbox(
        "Force refresh (re-download all chapters)",
        key="dl_force_refresh",
    )

    # ── Download button ────────────────────────────────────────────────
    if st.button("🚀 Start Download", type="primary", key="dl_download_btn"):
        log_area = st.empty()
        lines: list[str] = []

        def _log(msg):
            lines.append(str(msg))

        with st.spinner(f"Downloading {selected} docs…"):
            try:
                if is_inventory_product:
                    results = download_from_inventory(
                        selected, log=_log, force=force_refresh
                    )
                else:
                    results = _run_legacy_download(
                        selected, target_release.strip() or None,
                        _log, force=force_refresh,
                    )
            except Exception as exc:
                lines.append(f"\n❌ Error: {exc}")
                log_area.code("\n".join(lines), language="text")
                st.error(f"Download failed: {exc}")
                return

        log_area.code("\n".join(lines), language="text")
        ok_count = sum(1 for r in results if r[1])
        fail_count = sum(1 for r in results if not r[1])
        st.success(f"✅ Download complete — {ok_count} succeeded, {fail_count} failed")


def _run_legacy_download(product_key, target_release, log, force=False):
    """Run a legacy (non-inventory) download module."""
    entry = LEGACY_DOWNLOAD_REGISTRY[product_key]
    mod = importlib.import_module(entry["module"])
    kwargs = dict(
        download_dir=entry["folder"],
        target_release=target_release,
        log=log,
    )
    sig = inspect.signature(mod.run_download)
    if "force" in sig.parameters:
        kwargs["force"] = force
    return mod.run_download(**kwargs)


def _show_folder_stats(folder):
    """Display file-count stats for an output folder."""
    if os.path.isdir(folder):
        all_files = []
        for _r, _d, _f in os.walk(folder):
            all_files.extend(_f)
        pdfs = [f for f in all_files if f.endswith(".pdf")]
        mds = [f for f in all_files if f.endswith(".md")]
        parts = []
        if pdfs:
            parts.append(f"{len(pdfs)} PDF(s)")
        if mds:
            parts.append(f"{len(mds)} Markdown chapter(s)")
        if parts:
            st.caption(f"Currently {', '.join(parts)} in folder")
        else:
            st.caption("Folder is empty.")
    else:
        st.caption("Folder does not exist yet — will be created on download.")


# ═══════════════════════════════════════════════════════════════════════
# Section 3 — Rebuild Vector Store
# ═══════════════════════════════════════════════════════════════════════

def _render_rebuild_vector_store():
    st.subheader("🔄 Rebuild Vector Store")
    st.caption(
        "Rebuild the vector store from the current contents of `knowledge_docs/`. "
        "Use this after downloading new documentation or removing outdated files."
    )

    # Show current vector store stats
    try:
        from vector_store_manager import PERSIST_DIRECTORY, is_initialized
        db_path = os.path.join(PERSIST_DIRECTORY, "chroma.sqlite3")
        if os.path.exists(db_path):
            size_mb = os.path.getsize(db_path) / (1024 * 1024)
            st.caption(f"📂 Vector store: `{PERSIST_DIRECTORY}` ({size_mb:.0f} MB)")
        else:
            st.caption("📂 No existing vector store found — a fresh one will be created.")

        if is_initialized():
            from vector_store_manager import get_vector_store
            vs = get_vector_store()
            doc_count = vs._collection.count()
            st.caption(f"📊 Current document count: **{doc_count:,}**")
    except Exception:
        pass

    # Count knowledge_docs per product
    if os.path.isdir(KNOWLEDGE_DOCS_DIR):
        for product_folder in sorted(os.listdir(KNOWLEDGE_DOCS_DIR)):
            pf = os.path.join(KNOWLEDGE_DOCS_DIR, product_folder)
            if os.path.isdir(pf):
                all_pf = []
                for _rr, _dd, _ff in os.walk(pf):
                    all_pf.extend(_ff)
                pdfs = [f for f in all_pf if f.endswith(".pdf")]
                mds = [f for f in all_pf if f.endswith(".md")]
                htmls = [f for f in all_pf if f.endswith(".html") and not f.startswith("_")]
                txts = [f for f in all_pf if f.endswith(".txt")]
                parts = []
                if pdfs:  parts.append(f"{len(pdfs)} PDF")
                if htmls: parts.append(f"{len(htmls)} HTML")
                if mds:   parts.append(f"{len(mds)} MD")
                if txts:  parts.append(f"{len(txts)} TXT")
                st.caption(f"  • `{product_folder}/` — {', '.join(parts) if parts else 'empty'}")

    col1, col2 = st.columns([1, 1])
    with col1:
        confirm = st.checkbox(
            "I understand this will delete and rebuild the entire vector store",
            key="admin_reingest_confirm",
        )
    with col2:
        pass

    if st.button("🔄 Rebuild Vector Store", type="primary",
                 key="admin_reingest_btn", disabled=not confirm):
        _run_reingestion()


# ═══════════════════════════════════════════════════════════════════════
# Re-ingestion helper
# ═══════════════════════════════════════════════════════════════════════

def _run_reingestion():
    """Delete the existing vector store and rebuild from knowledge_docs/."""
    from vector_store_manager import (
        PERSIST_DIRECTORY, get_embeddings, supports_persistence,
        _vector_store, initialize_vector_store,
    )
    import vector_store_manager as vsm

    progress = st.empty()
    log_lines: list[str] = []

    def _log(msg):
        log_lines.append(str(msg))
        progress.code("\n".join(log_lines), language="text")

    try:
        # 1. Tear down existing store
        _log("🗑️  Removing existing vector store…")
        vsm._vector_store = None
        if os.path.exists(PERSIST_DIRECTORY):
            shutil.rmtree(PERSIST_DIRECTORY, ignore_errors=True)
            _log(f"   Deleted {PERSIST_DIRECTORY}")

        # 2. Also reset session state so the app picks up the new store
        st.session_state.pop("vector_store", None)
        st.session_state.pop("vector_store_initialized", None)

        # 3. Rebuild
        _log("🔄 Rebuilding vector store (this may take a few minutes)…")
        with st.spinner("Ingesting documents…"):
            vs = initialize_vector_store()
            doc_count = vs._collection.count()
            st.session_state.vector_store = vs
            st.session_state.vector_store_initialized = True

        _log(f"✅ Done — {doc_count:,} documents ingested")
        st.success(f"✅ Vector store rebuilt with {doc_count:,} documents")

    except Exception as exc:
        _log(f"❌ Error: {exc}")
        st.error(f"Re-ingestion failed: {exc}")

