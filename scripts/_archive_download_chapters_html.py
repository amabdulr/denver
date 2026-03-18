#!/usr/bin/env python3
"""
Download raw HTML for every chapter in the SD-WAN inventory, then
convert to Markdown for ingestion.

Thin wrapper around admin/download_sdwan_html.py so it can be run from
the scripts/ directory.

Usage:
    python scripts/download_chapters_html.py              # download + convert all
    python scripts/download_chapters_html.py --dry-run    # preview only
    python scripts/download_chapters_html.py --reconvert  # re-convert cached HTML
"""

import os
import sys

# Allow imports from the project root
SCRIPT_DIR = os.path.dirname(os.path.abspath(__file__))
PROJECT_ROOT = os.path.dirname(SCRIPT_DIR)
sys.path.insert(0, PROJECT_ROOT)

from admin.download_sdwan_html import run_download  # noqa: E402

if __name__ == "__main__":
    # Pass through to the admin module's __main__ handling
    exec(open(os.path.join(PROJECT_ROOT, "admin", "download_sdwan_html.py")).read())

