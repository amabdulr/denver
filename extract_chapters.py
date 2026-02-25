import os
import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor

# --- CONFIGURATION ---
INVENTORY_FILE = "knowledge_docs/sdwan/document_inventory.json"
OUTPUT_FILE = "knowledge_docs/sdwan/document_inventory.json"  # Overwrites with enriched data
MAX_WORKERS = 5
BASE_URL = "https://www.cisco.com"
# ---------------------

def extract_chapters(source_url):
    """Extract chapter names and slugs from a Cisco documentation book page."""
    try:
        res = requests.get(source_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')

        # The book slug is the last part of the URL path (without .html)
        book_slug = source_url.rstrip('/').split('/')[-1].replace('.html', '')

        chapters = []
        seen = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            text = a.get_text(strip=True)

            # Chapter links contain the book slug and end in .html
            if book_slug in href and text and len(text) > 3 and not href.endswith('.pdf'):
                full_url = urljoin(BASE_URL, href)
                if full_url in seen:
                    continue
                seen.add(full_url)

                chapter_slug = href.rstrip('/').split('/')[-1].replace('.html', '')
                # Skip the book's own landing page and login links
                if chapter_slug == book_slug or 'login' in href:
                    continue

                chapters.append({
                    "chapter_slug": chapter_slug,
                    "chapter_title": text,
                    "chapter_url": full_url
                })

        return chapters
    except Exception as e:
        print(f"  Error fetching {source_url}: {e}")
        return []


def process_book(item):
    """Process a single book entry: (filename, book_data)."""
    filename, book_data = item
    source_url = book_data.get("source_url", "")
    if not source_url:
        print(f"  SKIP (no URL): {filename}")
        return filename, []

    print(f"  Extracting: {filename}")
    chapters = extract_chapters(source_url)
    print(f"    Found {len(chapters)} chapters")
    return filename, chapters


def main():
    with open(INVENTORY_FILE, 'r') as f:
        inventory = json.load(f)

    print(f"Loaded {len(inventory)} books from inventory.\n")
    print("Extracting chapters in parallel...\n")

    items = list(inventory.items())

    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(process_book, items))

    # Enrich inventory with chapters
    for filename, chapters in results:
        inventory[filename]["chapters"] = chapters

    # Write enriched inventory
    with open(OUTPUT_FILE, 'w') as f:
        json.dump(inventory, f, indent=2)

    total_chapters = sum(len(ch) for _, ch in results)
    print(f"\nDone! {total_chapters} total chapters extracted across {len(inventory)} books.")
    print(f"Saved to: {OUTPUT_FILE}")


if __name__ == "__main__":
    main()
