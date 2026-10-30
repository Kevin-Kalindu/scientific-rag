from collections import defaultdict

from . import store
from .config import TEXT_COLLECTION, IMAGE_COLLECTION
from .embed import embed_query, embed_query_for_images


def rrf(rankings, k=60):
    scores, items = defaultdict(float), {}
    for ranking in rankings:
        for rank, point in enumerate(ranking, start=1):
            scores[point.id] += 1 / (k + rank)
            items[point.id] = point
    ordered = sorted(scores, key=scores.get, reverse=True)
    return [items[i] for i in ordered]


def retrieve(question, top_k=6, paper_id=None, use_images=True):
    rankings = [store.search(TEXT_COLLECTION, embed_query(question), limit=top_k * 2, paper_id=paper_id)]
    if use_images:
        rankings.append(store.search(IMAGE_COLLECTION, embed_query_for_images(question),
                                     limit=top_k * 2, paper_id=paper_id))
    return rrf(rankings)[:top_k]