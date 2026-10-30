import uuid
from dataclasses import dataclass, asdict


@dataclass
class Chunk:
    paper_id: str
    kind: str              # 'text' | 'table' | 'figure'
    page: int              # 1-based page number
    text: str              # what gets embedded: body text, table markdown or figure caption
    label: str = ''        # 'Figure 3', 'Table 2' (empty for body text)
    image_path: str = ''   # crop on disk, relative to ASSET_DIR (figures and tables only)
    title: str = ''

    @property
    def id(self):
        key = f'{self.paper_id}|{self.kind}|{self.page}|{self.label}|{self.text[:200]}'
        return str(uuid.uuid5(uuid.NAMESPACE_URL, key))

    def payload(self):
        return asdict(self)