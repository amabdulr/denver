import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

# --- CONFIGURATION ---
MAX_WORKERS = 5
DOWNLOAD_DIR = "knowledge_docs/iot"
LANDING_PAGE = "https://www.cisco.com/c/en/us/td/docs/iot/collections/iot-fnd-user-content-5-x-x.html"
BASE_URL = "https://www.cisco.com"
# ---------------------


def download_pdf(pdf_url):
    """Download a single PDF file."""
    try:
        file_name = pdf_url.split('/')[-1].split('?')[0]  # strip query params
        file_path = os.path.join(DOWNLOAD_DIR, file_name)

        if os.path.exists(file_path):
            print(f"  SKIP (already exists): {file_name}")
            return file_name

        print(f"  Downloading: {file_name}")
        with requests.get(pdf_url, stream=True, timeout=30) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        print(f"  ✅ DONE: {file_name}")
        return file_name
    except Exception as e:
        print(f"  ❌ Error downloading {pdf_url}: {e}")
        return None


def find_pdfs_on_page(page_url):
    """Scrape a page and return all PDF URLs found on it."""
    try:
        res = requests.get(page_url, timeout=15)
        soup = BeautifulSoup(res.text, 'html.parser')
        pdfs = set()
        for a in soup.find_all('a', href=True):
            href = a['href']
            if href.lower().endswith('.pdf'):
                pdfs.add(urljoin(page_url, href))
        return pdfs
    except Exception as e:
        print(f"  ⚠️  Could not fetch {page_url}: {e}")
        return set()


def run_download():
    os.makedirs(DOWNLOAD_DIR, exist_ok=True)

    print(f"Fetching landing page: {LANDING_PAGE}")
    res = requests.get(LANDING_PAGE, timeout=15)
    soup = BeautifulSoup(res.text, 'html.parser')

    # --- Step 1: Collect direct PDF links on the landing page ---
    all_pdf_urls = set()
    guide_pages = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(LANDING_PAGE, href)
        if href.lower().endswith('.pdf'):
            all_pdf_urls.add(full_url)
        elif '/td/docs/' in href and not href.endswith('.html#'):
            guide_pages.add(full_url)

    print(f"\nFound {len(all_pdf_urls)} direct PDF links on landing page")
    print(f"Found {len(guide_pages)} guide pages to check for more PDFs\n")

    # --- Step 2: Visit each guide page and scrape for PDF links ---
    print("Scanning guide pages for PDFs...")
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(find_pdfs_on_page, url): url for url in guide_pages}
        for future in as_completed(futures):
            pdfs = future.result()
            if pdfs:
                all_pdf_urls.update(pdfs)

    all_pdf_urls = sorted(all_pdf_urls)
    print(f"\nTotal unique PDFs to download: {len(all_pdf_urls)}\n")

    # --- Step 3: Download all PDFs in parallel ---
    downloaded = []
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        futures = {executor.submit(download_pdf, url): url for url in all_pdf_urls}
        for future in as_completed(futures):
            result = future.result()
            if result:
                downloaded.append(result)

    print(f"\n{'='*50}")
    print(f"Done! {len(downloaded)} PDFs saved to '{DOWNLOAD_DIR}'")


if __name__ == "__main__":
    run_download()