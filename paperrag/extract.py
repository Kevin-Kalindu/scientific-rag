import re
from dataclasses import dataclass

import fitz  # PyMuPDF (pip install pymupdf, NOT pip install fitz)

from .config import ASSET_DIR, CHUNK_WORDS, CHUNK_OVERLAP
from .models import Chunk

# Captions look like 'Figure 3:', 'Fig. 3.' or 'Table 2:'. Requiring a : . or |
# after the number avoids matching body text such as 'Figure 3 shows that...'
CAPTION_RE = re.compile(r'^\s*(Figure|Fig\.|Table)\s*(\d+)\s*[:.|]')
REFS_RE = re.compile(r'(\d+\.?\s*)?(references|bibliography)')


@dataclass
class Caption:
    kind: str        # 'Figure' or 'Table'
    label: str       # 'Figure 3'
    rect: fitz.Rect  # where the caption sits on the page
    text: str


def clean(text):
    text = text.replace('-\n', '')   # re-join words hyphenated across lines
    return ' '.join(text.split())    # collapse newlines and repeated spaces


def rel(path):
    return path.relative_to(ASSET_DIR).as_posix()   # store portable relative paths


def find_captions(blocks):
    caps = []
    for x0, y0, x1, y1, text, *_ in blocks:
        m = CAPTION_RE.match(text)
        if m:
            kind = 'Table' if m.group(1) == 'Table' else 'Figure'
            caps.append(Caption(kind, f'{kind} {m.group(2)}', fitz.Rect(x0, y0, x1, y1), clean(text)))
    return caps


def closest_caption(region, captions, kind, max_gap=60):
    best, best_gap = None, max_gap          # gap measured in points (72 = 1 inch)
    for c in captions:
        if c.kind != kind:
            continue
        gap = min(abs(c.rect.y0 - region.y1), abs(region.y0 - c.rect.y1))
        if gap < best_gap:
            best, best_gap = c, gap
    return best


def crop(page, rect, path, pad=4):
    clip = fitz.Rect(rect.x0 - pad, rect.y0 - pad, rect.x1 + pad, rect.y1 + pad) & page.rect
    page.get_pixmap(clip=clip, dpi=150).save(str(path))

def to_markdown(rows):
    rows = [[(cell or '').replace('\n', ' ').strip() for cell in row] for row in rows]
    header = '| ' + ' | '.join(rows[0]) + ' |'
    divider = '|' + '---|' * len(rows[0])
    body = ['| ' + ' | '.join(r) + ' |' for r in rows[1:]]
    return '\n'.join([header, divider] + body)


def extract_tables(page, captions):
    found = []
    for t in page.find_tables().tables:
        rows = t.extract()
        if len(rows) < 2 or len(rows[0]) < 2:
            continue                   
        rect = fitz.Rect(t.bbox)
        found.append((rect, closest_caption(rect, captions, 'Table'), to_markdown(rows)))
    return found


def extract_figures(page, captions):
    visuals = [fitz.Rect(i['bbox']) for i in page.get_image_info()]
    visuals += list(page.cluster_drawings()) 
    visuals = [r for r in visuals if r.width > 50 and 40 < r.height < page.rect.height * 0.8]
    found = []
    figs = sorted((c for c in captions if c.kind == 'Figure'), key=lambda c: c.rect.y0)
    for i, cap in enumerate(figs):
        floor = figs[i - 1].rect.y1 if i else 0     
        above = [r for r in visuals
                 if r.y1 <= cap.rect.y0 + 5 and r.y0 >= floor - 5
                 and r.x1 > cap.rect.x0 and r.x0 < cap.rect.x1]   
        if not above:
            continue
        above.sort(key=lambda r: r.y1, reverse=True)  
        region = fitz.Rect(above[0])
        for r in above[1:]:                        
            if r.y1 >= region.y0 - 20:
                region.include_rect(r)
            else:
                break
        found.append((cap, region))
    return found

def windows(paragraphs, size, overlap):
    words = [(w, pg) for pg, text in paragraphs for w in text.split()]
    step = size - overlap
    for start in range(0, len(words), step):
        window = words[start:start + size]
        if len(window) < 30:
            break              
        yield window[0][1], ' '.join(w for w, _ in window)


def parse_pdf(pdf_path, paper_id, title=''):
    out_dir = ASSET_DIR / paper_id
    out_dir.mkdir(parents=True, exist_ok=True)
    chunks, paragraphs, in_refs = [], [], False

    for page in fitz.open(pdf_path):
        n = page.number + 1                                        
        blocks = [b for b in page.get_text('blocks') if b[6] == 0]  
        captions = find_captions(blocks)
        skip = []                                                   

        for k, (rect, cap, md) in enumerate(extract_tables(page, captions)):
            img = out_dir / f'p{n}_table{k}.png'
            crop(page, rect, img)
            label = cap.label if cap else f'Table (page {n})'
            text = (cap.text + '\n\n' if cap else '') + md
            chunks.append(Chunk(paper_id, 'table', n, text, label, rel(img), title))
            skip += [rect] + ([cap.rect] if cap else [])

        for k, (cap, rect) in enumerate(extract_figures(page, captions)):
            img = out_dir / f'p{n}_fig{k}.png'
            crop(page, rect, img)
            chunks.append(Chunk(paper_id, 'figure', n, cap.text, cap.label, rel(img), title))
            skip += [rect, cap.rect]

        for x0, y0, x1, y1, text, *_ in blocks:
            r = fitz.Rect(x0, y0, x1, y1)
            t = clean(text)
            if REFS_RE.fullmatch(t.lower()):
                in_refs = True                                      
            if in_refs or not t or t.isdigit() or any(r.intersects(s) for s in skip):
                continue
            paragraphs.append((n, t))

    for n, text in windows(paragraphs, CHUNK_WORDS, CHUNK_OVERLAP):
        chunks.append(Chunk(paper_id, 'text', n, text, title=title))
    return chunks

