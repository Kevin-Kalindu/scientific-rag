from qdrant_client import QdrantClient
from qdrant_client.models import Distance, VectorParams, PointStruct, Filter, FieldCondition, MatchValue
from .config import DB_DIR, QDRANT_URL, TEXT_COLLECTION, IMAGE_COLLECTION, TEXT_DIM, IMAGE_DIM
_client = None

def client():
    global _client
    if _client is None:
        if QDRANT_URL:
            _client = QdrantClient(url=QDRANT_URL)         
        else:
            DB_DIR.mkdir(parents=True, exist_ok=True)
            _client = QdrantClient(path=str(DB_DIR))         
    return _client


def init_collections():
    for name, dim in [(TEXT_COLLECTION, TEXT_DIM), (IMAGE_COLLECTION, IMAGE_DIM)]:
        if not client().collection_exists(name):
            client().create_collection(name, vectors_config=VectorParams(size=dim, distance=Distance.COSINE))


def paper_filter(paper_id):
    return Filter(must=[FieldCondition(key='paper_id', match=MatchValue(value=paper_id))])


def upsert(collection, chunks, vectors):
    points = [PointStruct(id=c.id, vector=v.tolist(), payload=c.payload()) for c, v in zip(chunks, vectors)]
    client().upsert(collection, points=points)


def paper_ingested(paper_id):
    found, _ = client().scroll(TEXT_COLLECTION, scroll_filter=paper_filter(paper_id), limit=1)
    return len(found) > 0


def search(collection, vector, limit=10, paper_id=None):
    result = client().query_points(
        collection,
        query=vector.tolist(),
        query_filter=paper_filter(paper_id) if paper_id else None,
        limit=limit,
        with_payload=True,
    )
    return result.points