"""
Centralized path definitions for the Denver app.

All paths are relative to the project root (one level above app/).
Import PROJECT_ROOT and use os.path.join() to build paths.
"""

import os

# Project root is one level above this file's directory (app/)
PROJECT_ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

# Frequently used directories
PROMPTS_DIR = os.path.join(PROJECT_ROOT, "prompts")
CONFIG_DIR = os.path.join(PROJECT_ROOT, "config")
TEMPLATES_DIR = os.path.join(PROJECT_ROOT, "templates")
INVENTORY_DIR = os.path.join(PROJECT_ROOT, "inventory")
KNOWLEDGE_DOCS_DIR = os.path.join(PROJECT_ROOT, "knowledge_docs")
DATA_DIR = os.path.join(PROJECT_ROOT, "data")
SCOUR_OUTPUT_DIR = os.path.join(PROJECT_ROOT, "scour_output")
TESTS_DIR = os.path.join(PROJECT_ROOT, "tests")
