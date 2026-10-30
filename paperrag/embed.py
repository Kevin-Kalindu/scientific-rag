from functools import lru_cache
from PIL import Image  
from sentence_transformers import SentenceTransformer
from .config import ASSET_DIR, TEXT_MODEL, IMAGE_MODEL
QUERY_PREFIX = "Represent this sentence for searching relavant passages: "

@lru_cache(maxsize=None)
def text_model():
    return SentenceTransformer(TEXT_MODEL)

@lru_cache(maxsize=None)
def image_model():
    return SentenceTransformer(IMAGE_MODEL)

def embed_texts(texts, batch_size=32):
    return text_model().encode(texts, batch_size=batch_size, normalize_embeddings=True)

def embed_query(question):
    return text_model().encode(QUERY_PREFIX+ question, normalize_embeddings=True)

def embed_images(paths):
    images=[Image.open(ASSET_DIR /p).convert('RGB') for p in paths]
    return image_model().encode(images, batch_size=16, normalize_embeddings=True)

def embed_query_for_images(question):
    return image_model().encode(question, normalize_embeddings=True)