import argparse
import json
import logging

from tqdm import tqdm

from . import store
from .config import PDF_DIR, META, TEXT_COLLECTION, IMAGE_COLLECTION
from .embed import embed_texts, embed_images
from .extract import parse_pdf

log = logging.getLogger('ingest')


def ingest_pdf(path, paper_id, title='', force=False):
    if not force and store.paper_ingested(paper_id):
        log.info('skip %s (already ingested)', paper_id)
        return 0

    chunks = parse_pdf(path, paper_id, title)                  
    if not chunks:
        log.warning('no chunks from %s (scanned PDF?)', paper_id)
        return 0
    
    store.upsert(TEXT_COLLECTION, chunks, embed_texts([c.text for c in chunks]))
    visual = [c for c in chunks if c.image_path]
    if visual:
        store.upsert(IMAGE_COLLECTION, visual, embed_images([c.image_path for c in visual]))

    kinds = {k: sum(c.kind == k for c in chunks) for k in ('text', 'table', 'figure')}
    log.info('ingested %s: %s', paper_id, kinds)
    return len(chunks)


def main():
    parser = argparse.ArgumentParser(description='Ingest every PDF in data/pdfs')
    parser.add_argument('--force', action='store_true', help='re-ingest even if already present')
    args = parser.parse_args()
    logging.basicConfig(level=logging.INFO, format='%(levelname)s %(message)s')

    store.init_collections()
    meta = json.loads(META.read_text()) if META.exists() else {}
    for pdf in tqdm(sorted(PDF_DIR.glob('*.pdf'))):
        ingest_pdf(pdf, pdf.stem, meta.get(pdf.stem, pdf.stem), args.force)


if __name__ == '__main__':
    main()