# paperrag/download.py
import json
import sys
import time
import arxiv
import requests
from .config import PDF_DIR, META

HEADERS = {'User-Agent': 'paperrag-student-project (personal research use)'}

def fetch_pdf(url, dest):
    r = requests.get(url, headers=HEADERS, timeout=60, allow_redirects=True)
    r.raise_for_status()
    dest.write_bytes(r.content)

def download(ids=None, query=None, max_results=5):
    PDF_DIR.mkdir(parents=True, exist_ok=True)
    meta = json.loads(META.read_text()) if META.exists() else {}
    search = arxiv.Search(id_list=ids) if ids else arxiv.Search(query=query, max_results=max_results)
    client = arxiv.Client(delay_seconds=3, num_retries=3)   
    for result in client.results(search):
        paper_id = result.get_short_id().replace('/', '_')   
        pdf = PDF_DIR / f'{paper_id}.pdf'
        if not pdf.exists():                                  
            fetch_pdf(result.pdf_url, pdf)
            time.sleep(3)                                     
        meta[paper_id] = result.title
        print('ok', paper_id, result.title)
    META.write_text(json.dumps(meta, indent=2))

if __name__ == '__main__':
    download(ids=sys.argv[1:])