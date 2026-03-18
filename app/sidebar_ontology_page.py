"""
Ontology Page — sidebar page for managing per-product guide mappings.

Each product has its own guide_mappings.json under
  ontology/<product>/guide_mappings.json
Shared (cross-product) settings live in
  ontology/_shared/guide_mappings.json

Editable product-specific sections:
  • Reference Guides
  • Concept → Guide Mapping
  • Product Noise Words

Editable shared sections:
  • Install / Upgrade Terms
  • Filename Noise Words
  • Stop Words
"""

import os
import json
import shutil
import streamlit as st
from paths import ONTOLOGY_DIR, INVENTORY_DIR

# ── Section definitions ────────────────────────────────────────────────
# (key, label, description, scope)  scope = "product" | "shared"
_EDITABLE_SECTIONS = [
    ("concept_to_guide",       "🔗 Concept → Guide Mapping", "Maps technology terms to guide filename patterns.",  "product"),
    ("product_noise",          "🔇 Product Noise Words",     "Terms to skip during matching for this product.",    "product"),
    ("reference_guides",       "📋 Reference Guides",        "Guides excluded from auto-selection.",               "product"),
    ("document_inventory",     "📦 Document Inventory",      "PDF → title / source URL / chapters inventory.",     "inventory"),
    ("install_upgrade_terms",  "⬆️ Install / Upgrade Terms", "Terms that trigger install/upgrade guide selection.", "shared"),
    ("filename_noise_words",   "📝 Filename Noise Words",    "Common words in filenames to ignore.",               "shared"),
    ("stop_words",             "🛑 Stop Words",              "English stop words stripped before matching.",        "shared"),
]


def _discover_products():
    """Return sorted list of product folder names under ontology/."""
    if not os.path.isdir(ONTOLOGY_DIR):
        return []
    return sorted(
        d for d in os.listdir(ONTOLOGY_DIR)
        if os.path.isdir(os.path.join(ONTOLOGY_DIR, d)) and d != "_shared"
    )


def _resolve_path(product_code: str, scope: str) -> str:
    """Return the JSON file path for a given product + scope."""
    if scope == "shared":
        return os.path.join(ONTOLOGY_DIR, "_shared", "guide_mappings.json")
    if scope == "inventory":
        return os.path.join(INVENTORY_DIR, product_code, "document_inventory.json")
    return os.path.join(ONTOLOGY_DIR, product_code, "guide_mappings.json")


def _load_json(path: str) -> dict:
    try:
        with open(path, "r") as f:
            return json.load(f)
    except Exception:
        return {}


def _save_json(path: str, data: dict):
    bak = path + ".bak"
    if os.path.exists(path):
        shutil.copy2(path, bak)
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w") as f:
        json.dump(data, f, indent=4, ensure_ascii=False)


def _render_section_editor(product_code: str):
    """Render the JSON editor for the selected product."""
    # Build section list
    section_labels = {key: label for key, label, _, _ in _EDITABLE_SECTIONS}
    section_help = {key: desc for key, _, desc, _ in _EDITABLE_SECTIONS}
    section_scope = {key: scope for key, _, _, scope in _EDITABLE_SECTIONS}

    # Only show sections whose source file exists and contains data
    available = []
    for key, _, _, scope in _EDITABLE_SECTIONS:
        path = _resolve_path(product_code, scope)
        if scope == "inventory":
            if os.path.isfile(path):
                available.append(key)
        else:
            data = _load_json(path)
            if key in data:
                available.append(key)
    if not available:
        st.warning(f"No editable sections found for **{product_code}**.")
        return

    selected_section = st.selectbox(
        "Section to edit",
        options=available,
        format_func=lambda k: f"{section_labels[k]}  {'(shared)' if section_scope[k] == 'shared' else ''}",
        key=f"kg_section_{product_code}",
    )

    scope = section_scope[selected_section]
    file_path = _resolve_path(product_code, scope)
    data = _load_json(file_path)
    is_standalone = scope == "inventory"

    if scope == "shared":
        st.info("ℹ️ This is a **shared** setting — changes apply to all products.")
    st.caption(section_help.get(selected_section, ""))
    st.caption(f"📂 File: `{file_path}`")

    if is_standalone:
        section_data = data
    else:
        section_data = data.get(selected_section, {})
    section_json = json.dumps(section_data, indent=4, ensure_ascii=False)

    edited_json = st.text_area(
        f"Edit JSON for **{section_labels.get(selected_section, selected_section)}**",
        value=section_json,
        height=400,
        key=f"kg_editor_{product_code}_{selected_section}",
    )

    col_save, col_reset = st.columns([1, 1])
    with col_save:
        if st.button("💾 Save Changes", type="primary", key=f"kg_save_{product_code}"):
            try:
                parsed = json.loads(edited_json)
                if is_standalone:
                    _save_json(file_path, parsed)
                else:
                    data[selected_section] = parsed
                    _save_json(file_path, data)
                st.success(f"✅ Saved `{selected_section}` — backup at `.bak`")
            except json.JSONDecodeError as e:
                st.error(f"❌ Invalid JSON: {e}")

    with col_reset:
        if st.button("↩️ Revert to Saved", key=f"kg_revert_{product_code}"):
            st.session_state.pop(f"kg_editor_{product_code}_{selected_section}", None)
            st.rerun()


def render_ontology_page():
    """Main entry point for the Ontology page."""
    st.header("🧠 Ontology")
    st.caption(
        "Per-product guide mappings that control how detected technology "
        "terms map to PDF guide filenames. Each product has its own config."
    )

    products = _discover_products()
    if not products:
        st.warning("No product folders found under `ontology/`.")
        return

    product_code = st.selectbox(
        "Select product",
        options=products,
        key="kg_product_selector",
    )

    st.markdown("---")
    _render_section_editor(product_code)
