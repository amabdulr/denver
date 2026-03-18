"""
Inventory Manager — CRUD operations on product document inventories.

Provides helpers for:
  - Loading / saving inventory JSON files
  - Scraping URLs to build an inventory (delegates to product scripts)
  - Removing books from an inventory
  - Listing products that have inventories

Used by the Admin UI (sidebar_admin_page.py).
"""

import importlib
import json
import os
from typing import Optional

SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
INVENTORY_BASE = os.path.join(PROJECT_ROOT, "inventory")

# ── Product registry ────────────────────────────────────────────────────
# Products that use a document_inventory.json file.
# "module"      — download module that has build_inventory() / _download_and_convert()
# "inv_dir"     — subfolder under inventory/
# "has_scraper" — True if the module exposes build_inventory()
# "supports_release" — True if scraper accepts target_release
# "release_placeholder" — hint text for the release input

PRODUCT_CONFIGS = {
    "Cisco 8000": {
        "module": "admin.download_cisco8000",
        "inv_dir": "Cisco8000",
        "has_scraper": True,
        "supports_release": True,
        "release_placeholder": "e.g. 26 for 26xx (RECOMMENDED to avoid duplicates)",
    },
    "ASR 9000": {
        "module": "admin.download_asr9000",
        "inv_dir": "ASR9000",
        "has_scraper": True,
        "supports_release": True,
        "release_placeholder": "e.g. 26 for 26xx (RECOMMENDED to avoid duplicates)",
    },
    "SD-WAN (HTML)": {
        "module": "admin.download_sdwan_html",
        "inv_dir": "sdwan",
        "has_scraper": False,
        "supports_release": False,
        "release_placeholder": "",
    },
}


def inventory_path(product_key: str) -> Optional[str]:
    """Return the full path to the product's document_inventory.json, or None."""
    cfg = PRODUCT_CONFIGS.get(product_key)
    if not cfg:
        return None
    return os.path.join(INVENTORY_BASE, cfg["inv_dir"], "document_inventory.json")


def load_inventory(product_key: str) -> dict:
    """Load and return the inventory dict.  Returns {} if no file exists."""
    path = inventory_path(product_key)
    if path and os.path.exists(path):
        with open(path, encoding="utf-8") as fh:
            return json.load(fh)
    return {}


def save_inventory(product_key: str, data: dict) -> str:
    """Write *data* to the product's inventory JSON.  Returns the path written."""
    path = inventory_path(product_key)
    if not path:
        raise ValueError(f"No inventory path configured for '{product_key}'")
    os.makedirs(os.path.dirname(path), exist_ok=True)
    with open(path, "w", encoding="utf-8") as fh:
        json.dump(data, fh, indent=2)
    return path


def remove_books(product_key: str, keys_to_remove: list) -> dict:
    """Remove *keys_to_remove* from the inventory and save.  Returns updated dict."""
    data = load_inventory(product_key)
    for key in keys_to_remove:
        data.pop(key, None)
    save_inventory(product_key, data)
    return data


def inventory_stats(product_key: str) -> tuple[int, int]:
    """Return (num_books, num_chapters) for a product inventory."""
    data = load_inventory(product_key)
    books = len(data)
    chapters = sum(len(v.get("chapters", [])) for v in data.values())
    return books, chapters


def scrape_inventory(product_key: str, target_release: Optional[str] = None,
                     log=print) -> dict:
    """Scrape cisco.com and build a fresh inventory for *product_key*.

    Delegates to the product module's ``build_inventory()`` function.
    Returns the inventory dict (also saved to disk by the module).
    """
    cfg = PRODUCT_CONFIGS.get(product_key)
    if not cfg or not cfg["has_scraper"]:
        raise ValueError(f"'{product_key}' does not support scraping")
    mod = importlib.import_module(cfg["module"])
    return mod.build_inventory(target_release=target_release, log=log)


def download_from_inventory(product_key: str, log=print,
                            book_filter: Optional[str] = None,
                            force: bool = False) -> list:
    """Download + convert using the saved inventory (no re-scraping).

    Returns list[(name, success_bool, message)].
    """
    cfg = PRODUCT_CONFIGS.get(product_key)
    if not cfg:
        raise ValueError(f"Unknown product '{product_key}'")
    mod = importlib.import_module(cfg["module"])

    # For modules that have download_from_inventory(), use it directly.
    if hasattr(mod, "download_from_inventory"):
        return mod.download_from_inventory(
            log=log, book_filter=book_filter, force=force
        )

    # Fallback: call run_download (e.g. SD-WAN HTML already reads from disk)
    return mod.run_download(log=log, book_filter=book_filter, force=force)
