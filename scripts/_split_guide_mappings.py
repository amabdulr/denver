"""One-time script: split config/guide_mappings.json into per-product files."""
import json, os, sys

PROJECT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SRC = os.path.join(PROJECT, "config", "guide_mappings.json")
KG_DIR = os.path.join(PROJECT, "ontology")

with open(SRC) as f:
    data = json.load(f)

# ── Shared sections (product-independent) ──
shared = {
    "_comment": "Shared knowledge-graph settings used by all products.",
    "install_upgrade_terms": data.get("install_upgrade_terms", {}),
    "filename_noise_words": data.get("filename_noise_words", {}),
    "stop_words": data.get("stop_words", {}),
}

shared_dir = os.path.join(KG_DIR, "_shared")
os.makedirs(shared_dir, exist_ok=True)
shared_file = os.path.join(shared_dir, "guide_mappings.json")
with open(shared_file, "w") as f:
    json.dump(shared, f, indent=4, ensure_ascii=False)
print(f"Wrote {shared_file} ({os.path.getsize(shared_file)} bytes)")

# ── Per-product sections ──
concept_to_guide = data.get("concept_to_guide", {})
product_noise_cfg = data.get("product_noise", {})
ref_cfg = data.get("reference_guides", {})
ref_patterns_raw = ref_cfg.get("patterns", {})

# Discover all product codes
products = set()
for k, v in concept_to_guide.items():
    if not k.startswith("_") and isinstance(v, dict):
        products.add(k)
for k in product_noise_cfg:
    if not k.startswith("_"):
        products.add(k)

print(f"Products found: {sorted(products)}")

for product_code in sorted(products):
    prod_dir = os.path.join(KG_DIR, product_code)
    os.makedirs(prod_dir, exist_ok=True)

    prod_data = {
        "_comment": f"Knowledge-graph mappings for {product_code}.",
        "concept_to_guide": concept_to_guide.get(product_code, {}),
        "product_noise": product_noise_cfg.get(product_code, []),
    }

    if isinstance(ref_patterns_raw, dict):
        prod_data["reference_guides"] = {
            "patterns": ref_patterns_raw.get(product_code, [])
        }
    else:
        prod_data["reference_guides"] = {
            "patterns": ref_patterns_raw if isinstance(ref_patterns_raw, list) else []
        }

    prod_file = os.path.join(prod_dir, "guide_mappings.json")
    with open(prod_file, "w") as f:
        json.dump(prod_data, f, indent=4, ensure_ascii=False)
    lines = json.dumps(prod_data, indent=4).count("\n") + 1
    print(f"Wrote {prod_file} ({lines} lines)")

print("\nDone! Original config/guide_mappings.json is still intact as fallback.")
