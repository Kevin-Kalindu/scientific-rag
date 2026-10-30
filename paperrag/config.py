import os
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
DATA = ROOT / 'data'
PDF_DIR = DATA / 'pdfs'
ASSET_DIR = DATA / 'assets'        # cropped figure and table images
DB_DIR = DATA / 'qdrant'           # vector database files (embedded mode)
META = DATA / 'papers.json'        # paper_id -> title
QDRANT_URL = os.getenv('QDRANT_URL')   
TEXT_MODEL = 'BAAI/bge-small-en-v1.5' 
IMAGE_MODEL = 'clip-ViT-B-32'         
TEXT_DIM, IMAGE_DIM = 384, 512
TEXT_COLLECTION = 'paper_text'
IMAGE_COLLECTION = 'paper_images'
CHUNK_WORDS = 200                      
CHUNK_OVERLAP = 40
LLM_MODEL = 'gamma3:4b' 