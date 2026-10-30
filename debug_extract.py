import sys, os, traceback
from collections import Counter
print('1. python:', sys.executable, flush=True)
print('2. cwd:', os.getcwd(), flush=True)
pdf = sys.argv[1] if len(sys.argv) > 1 else 'data/pdfs/1706.03762v7.pdf'
print('3. pdf exists:', os.path.exists(pdf), flush=True)
try:
    import fitz
    print('4. fitz imported, has open():', hasattr(fitz, 'open'), '| version:', getattr(fitz, 'VersionBind', '?'), flush=True)
    from paperrag import extract
    print('5. extract imported from:', extract.__file__, flush=True)
    from paperrag.config import ASSET_DIR
    print('6. ASSET_DIR:', ASSET_DIR, flush=True)
    doc = fitz.open(pdf)
    print('7. pages in pdf:', len(doc), flush=True)
    for page in doc:
        n = page.number + 1
        blocks = [b for b in page.get_text('blocks') if b[6] == 0]
        caps = extract.find_captions(blocks)
        tabs = extract.extract_tables(page, caps)
        figs = extract.extract_figures(page, caps)
        print('   page', n, '| text blocks:', len(blocks), '| captions:', [c.label for c in caps],
              '| tables:', len(tabs), '| figures:', [c.label for c, _ in figs], flush=True)
        if n >= 6:
            break
    print('8. running full parse_pdf ...', flush=True)
    chunks = extract.parse_pdf(pdf, 'test')
    print('9. chunk counts:', Counter(c.kind for c in chunks), flush=True)
    out = ASSET_DIR / 'test'
    print('10. output folder exists:', out.exists(), '| files:', sorted(os.listdir(out)) if out.exists() else None, flush=True)
except Exception:
    print('FAILED with this error:', flush=True)
    traceback.print_exc()
