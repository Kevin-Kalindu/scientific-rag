import sys
from collections import Counter
from paperrag.extract import parse_pdf

chunks = parse_pdf(sys.argv[1], 'test')
print(Counter(c.kind for c in chunks))
for c in chunks:
    if c.kind != 'text':
        print(c.kind, c.label, 'page', c.page, '->', c.image_path)