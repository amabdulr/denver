"""
One-off script to extract chapters for systems-interfaces-book-xe-sdwan.pdf
from Cisco.com and update document_inventory.json.
"""

import json
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin

BOOK_URL = "https://www.cisco.com/c/en/us/td/docs/routers/sdwan/configuration/system-interface/ios-xe-17/systems-interfaces-book-xe-sdwan.html"
BOOK_KEY = "systems-interfaces-book-xe-sdwan.pdf"
INVENTORY_FILE = "inventory/sdwan/document_inventory.json"
BASE_URL = "https://www.cisco.com"

def extract_chapters(source_url):
    book_slug = source_url.rstrip('/').split('/')[-1].replace('.html', '')

    res = requests.get(source_url, timeout=15, verify=False)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, 'html.parser')

    chapters = []
    seen = set()
    for a in soup.find_all('a', href=True):
        href = a['href']
        text = a.get_text(strip=True)

        if book_slug in href and text and len(text) > 3 and not href.endswith('.pdf'):
            full_url = urljoin(BASE_URL, href)
            if full_url in seen:
                continue
            seen.add(full_url)

            chapter_slug = href.rstrip('/').split('/')[-1].replace('.html', '')
            if chapter_slug == book_slug or 'login' in href:
                continue

            chapters.append({
                "chapter_slug": chapter_slug,
                "chapter_title": text,
                "chapter_url": full_url
            })

    return chapters


def main():
    print(f"Fetching: {BOOK_URL}\n")
    chapters = extract_chapters(BOOK_URL)

    if not chapters:
        print("ERROR: No chapters found. The page may have redirected.")
        return

    print(f"Found {len(chapters)} chapters:\n")
    for i, ch in enumerate(chapters, 1):
        print(f"  {i:2d}. {ch['chapter_title']}")
        print(f"      slug: {ch['chapter_slug']}")
        print(f"      url:  {ch['chapter_url']}")
        print()

    # Update inventory
    with open(INVENTORY_FILE, 'r') as f:
        inventory = json.load(f)

    old_count = len(inventory[BOOK_KEY].get('chapters', []))
    inventory[BOOK_KEY]['chapters'] = chapters

    with open(INVENTORY_FILE, 'w') as f:
        json.dump(inventory, f, indent=2)

    print(f"Updated {INVENTORY_FILE}: {old_count} → {len(chapters)} chapters for {BOOK_KEY}")


if __name__ == "__main__":
    main()
