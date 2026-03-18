"""
Admin download script — Cisco SD-WAN documentation PDFs.

Scrapes the Cisco SD-WAN product support page, follows every
guide link, and downloads the PDF for each guide.

Can be used standalone or called from the Admin UI.
"""

import os
import re
import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin
from concurrent.futures import ThreadPoolExecutor
from packaging import version

MAX_WORKERS = 5
BASE_URL = "https://www.cisco.com"
LANDING_PAGE = "https://www.cisco.com/c/en/us/support/routers/sd-wan/series.html"


def get_latest_version(soup):
    version_pattern = re.compile(r'(\d+\.\d+\.[\dx]+)')
    found_versions = []
    for text in soup.stripped_strings:
        match = version_pattern.search(text)
        if match:
            v_str = match.group(1).replace('x', '0')
            try:
                found_versions.append((version.parse(v_str), match.group(1)))
            except Exception:
                continue
    return sorted(found_versions, key=lambda x: x[0], reverse=True)[0][1] if found_versions else None


def _download_single_pdf(args):
    """Download a single PDF from a guide page.  Returns (filename, ok, msg)."""
    guide_url, download_dir = args
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
            file_path = os.path.join(download_dir, file_name)

            if os.path.exists(file_path):
                return (file_name, True, "already exists")

            with requests.get(pdf_url, stream=True, timeout=60) as r:
                r.raise_for_status()
                with open(file_path, 'wb') as f:
                    for chunk in r.iter_content(chunk_size=8192):
                        f.write(chunk)
            return (file_name, True, "downloaded")
        else:
            return (guide_url, False, "no PDF link found")
    except Exception as e:
        return (guide_url, False, str(e))


def run_download(download_dir="knowledge_docs/sdwan", target_release=None, log=print):
    """
    Scrape the SD-WAN landing page and download all guide PDFs.

    Args:
        download_dir:    Where to save the PDFs.
        target_release:  e.g. "20.15" to filter, or None for all.
        log:             Callable(str) for progress messages (default: print).

    Returns:
        list[tuple]: [(filename, success_bool, message), ...]
    """
    os.makedirs(download_dir, exist_ok=True)

    log("Fetching landing page…")
    soup = BeautifulSoup(requests.get(LANDING_PAGE, timeout=15).text, 'html.parser')

    if target_release:
        log(f"Targeting release: {target_release}")
    else:
        log("No release filter — downloading all guides.")

    # Collect guide links
    links = set()
    for link in soup.find_all('a', href=True):
        href = link['href']
        if '/td/docs/' not in href:
            continue
        # Skip release notes and system-message guides
        if 'release/notes' in href:
            continue
        if 'system-message-guide' in href or 'syslogs' in href:
            continue
        if target_release is None or target_release in (link.get_text() + href):
            links.add(urljoin(BASE_URL, href))

    log(f"Found {len(links)} guide(s). Starting download…")

    results = []
    args = [(url, download_dir) for url in links]
    with ThreadPoolExecutor(max_workers=MAX_WORKERS) as pool:
        for result in pool.map(_download_single_pdf, args):
            results.append(result)
            name, ok, msg = result
            status = "✅" if ok else "❌"
            log(f"  {status} {name}  ({msg})")

    downloaded = [r for r in results if r[1]]
    log(f"\nDone — {len(downloaded)}/{len(results)} PDFs in '{download_dir}'")
    return results


if __name__ == "__main__":
    run_download()
