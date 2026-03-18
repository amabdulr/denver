"""
Admin download script — Cisco IoT documentation PDFs.

Scrapes a Cisco IoT collection page, follows every guide link,
and downloads the PDF for each guide.

Can be used standalone or called from the Admin UI.
"""

import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor, as_completed

MAX_WORKERS = 5
BASE_URL = "https://www.cisco.com"
LANDING_PAGE = "https://www.cisco.com/c/en/us/td/docs/iot/collections/iot-fnd-user-content-5-x-x.html"


def _download_pdf(args):
    """Download a single PDF.  Returns (filename, ok, msg)."""
    pdf_url, download_dir = args
    try:
        file_name = pdf_url.split('/')[-1].split('?')[0]
        file_path = os.path.join(download_dir, file_name)

        if os.path.exists(file_path):
            return (file_name, True, "already exists")

        with requests.get(pdf_url, stream=True, timeout=60) as r:
            r.raise_for_status()
            with open(file_path, 'wb') as f:
                for chunk in r.iter_content(chunk_size=8192):
                    f.write(chunk)
        return (file_name, True, "downloaded")
    except Exception as e:
        return (pdf_url, False, str(e))


def _find_pdfs_on_page(page_url):
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
    except Exception:
        return set()


def run_download(download_dir="knowledge_docs/iot", target_release=None, log=print):
    """
    Scrape the IoT collection page and download all guide PDFs.

    Args:
        download_dir:    Where to save the PDFs.
        target_release:  Currently unused for IoT (kept for interface parity).
        log:             Callable(str) for progress messages.

    Returns:
        list[tuple]: [(filename, success_bool, message), ...]
    """
    os.makedirs(download_dir, exist_ok=True)

    log(f"Fetching landing page: {LANDING_PAGE}")
    res = requests.get(LANDING_PAGE, timeout=15)
    soup = BeautifulSoup(res.text, 'html.parser')

    all_pdf_urls = set()
    guide_pages = set()

    for a in soup.find_all('a', href=True):
        href = a['href']
        full_url = urljoin(LANDING_PAGE, href)
        if href.lower().endswith('.pdf'):
            all_pdf_urls.add(full_url)
        elif '/td/docs/' in href and not href.endswith('.html#'):
            guide_pages.add(full_url)

    log(f"Found {len(all_pdf_urls)} direct PDF links, {len(guide_pages)} guide pages to scan")

    # Visit each guide page for more PDFs
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        futures = {pool.submit(_find_pdfs_on_page, url): url for url in guide_pages}
        for future in as_completed(futures):
            pdfs = future.result()
            if pdfs:
                all_pdf_urls.update(pdfs)

    log(f"Total unique PDFs: {len(all_pdf_urls)}")

    results = []
    args = [(url, download_dir) for url in sorted(all_pdf_urls)]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for result in pool.map(_download_pdf, args):
            results.append(result)
            name, ok, msg = result
            status = "✅" if ok else "❌"
            log(f"  {status} {name}  ({msg})")

    downloaded = [r for r in results if r[1]]
    log(f"\nDone — {len(downloaded)}/{len(results)} PDFs in '{download_dir}'")
    return results


if __name__ == "__main__":
    run_download()
