import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from packaging import version

# --- CONFIGURATION ---
TARGET_RELEASE = None  # Set to None to download all guides, or a string like "17.15" to filter
MAX_WORKERS = 5           # Number of simultaneous downloads (don't go too high or you might get blocked)
DOWNLOAD_DIR = "knowledge_docs/sdwan"
# ---------------------

BASE_URL = "https://www.cisco.com"
LANDING_PAGE = "https://www.cisco.com/c/en/us/support/routers/sd-wan/series.html"

def get_latest_version(soup):
    version_pattern = re.compile(r'(\d+\.\d+\.[\dx]+)')
    found_versions = []
    for text in soup.stripped_strings:
        match = version_pattern.search(text)
        if match:
            v_str = match.group(1).replace('x', '0')
            try: found_versions.append((version.parse(v_str), match.group(1)))
            except: continue
    return sorted(found_versions, key=lambda x: x[0], reverse=True)[0][1] if found_versions else None

def download_single_pdf(guide_url):
    """Function to find and download a PDF from a single guide page."""
    try:
        res = requests.get(guide_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        
        pdf_url = None
        for a in soup.find_all('a', href=True):
            if a['href'].lower().endswith('.pdf'):
                pdf_url = urljoin(guide_url, a['href'])
                break
        
        if pdf_url:
            file_name = pdf_url.split('/')[-1]
            file_path = os.path.join(DOWNLOAD_DIR, file_name)
            
            # Use streaming to download large files efficiently
            print(f"Starting: {file_name}")
            with requests.get(pdf_url, stream=True) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            print(f"DONE: {file_name}")
        else:
            print(f"No PDF found for: {guide_url}")
    except Exception as e:
        print(f"Error downloading {guide_url}: {e}")

def run_fast_download(target_rel=None):
    if not os.path.exists(DOWNLOAD_DIR):
        os.makedirs(DOWNLOAD_DIR)

    print("Fetching landing page...")
    soup = BeautifulSoup(requests.get(LANDING_PAGE).text, 'html.parser')
    
    if target_rel:
        rel = target_rel
        print(f"Targeting Release: {rel}")
    else:
        rel = None
        print("No release filter — downloading all guides.")

    # Only include this specific release note
    KEEP_RELEASE_NOTE = "https://www.cisco.com/c/en/us/td/docs/routers/sdwan/release/notes/20-15/rel-notes-controllers-20-15.html"

    # Collect all matching guide links (skip release notes except the one above)
    links_to_process = [KEEP_RELEASE_NOTE]
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/td/docs/' in href:
            full_url = urljoin(BASE_URL, href)
            # Skip release notes (already added the one we want)
            if 'release/notes' in href:
                continue
            # Skip system message guides
            if 'system-message-guide' in href or 'syslogs' in href:
                continue
            if rel is None or rel in (link.get_text() + href):
                links_to_process.append(full_url)
    
    links_to_process = list(set(links_to_process))
    print(f"Found {len(links_to_process)} guides. Starting parallel download...\n")

    # Use ThreadPoolExecutor for parallel processing
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        executor.map(download_single_pdf, links_to_process)

    print(f"\nAll tasks complete. Files saved in '{DOWNLOAD_DIR}'")

if __name__ == "__main__":
    run_fast_download(TARGET_RELEASE)