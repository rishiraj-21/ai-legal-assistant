import logging
from collections import defaultdict

from app.retrieval.bm25_service import bm25_service
from app.retrieval.reranker import reranker
from app.services.embedding_service import embedding_service
from config import settings

logger = logging.getLogger(__name__)

RRF_K = 60  # Standard RRF constant


def _doc_key(doc: dict) -> str:
    """Create a unique key for a document to merge across retrievers."""
    meta = doc.get("metadata", {})
    doc_id = meta.get("document_id", "")
    chunk_idx = meta.get("chunk_index", "")
    if doc_id:
        return f"{doc_id}:{chunk_idx}"
    # Fallback: use first 100 chars of text as key
    return doc["text"][:100]


def reciprocal_rank_fusion(
    ranked_lists: list[list[dict]], k: int = RRF_K
) -> list[dict]:
    """
    Reciprocal Rank Fusion: score(d) = Σ 1/(k + rank_r(d))
    Rank-based, scale-invariant fusion of multiple ranked result lists.
    """
    scores: dict[str, float] = defaultdict(float)
    doc_map: dict[str, dict] = {}

    for ranked_list in ranked_lists:
        for rank, doc in enumerate(ranked_list):
            key = _doc_key(doc)
            scores[key] += 1.0 / (k + rank + 1)  # rank is 0-indexed, add 1
            if key not in doc_map:
                doc_map[key] = doc

    # Sort by RRF score descending
    sorted_keys = sorted(scores.keys(), key=lambda k: scores[k], reverse=True)

    results = []
    for key in sorted_keys:
        doc = dict(doc_map[key])
        doc["rrf_score"] = scores[key]
        results.append(doc)

    return results


class HybridRetriever:
    """
    Hybrid retrieval pipeline:
    1. FAISS dense → top-20
    2. BM25 sparse → top-20
    3. RRF fusion → merged top-20
    4. Cross-encoder re-rank → final top-5
    """

    def __init__(self):
        self._dense_k = 20
        self._sparse_k = 20
        self._rrf_top = 20

    def search(self, query: str, top_k: int | None = None) -> list[dict]:
        """Run full hybrid retrieval pipeline."""
        top_k = top_k or settings.reranker_top_k

        ranked_lists = []

        # 1. Dense retrieval (FAISS)
        faiss_results = embedding_service.search(query, k=self._dense_k)
        if faiss_results:
            ranked_lists.append(faiss_results)
            logger.debug("FAISS returned %d results", len(faiss_results))

        # 2. Sparse retrieval (BM25)
        if bm25_service.is_loaded:
            bm25_results = bm25_service.search(query, k=self._sparse_k)
            if bm25_results:
                ranked_lists.append(bm25_results)
                logger.debug("BM25 returned %d results", len(bm25_results))

        if not ranked_lists:
            logger.warning("No retrieval results from any source.")
            return []

        # 3. RRF fusion
        if len(ranked_lists) > 1:
            fused = reciprocal_rank_fusion(ranked_lists)[:self._rrf_top]
            logger.debug("RRF fused %d results", len(fused))
        else:
            fused = ranked_lists[0][:self._rrf_top]

        # 4. Cross-encoder re-ranking
        if reranker.is_loaded:
            results = reranker.rerank(query, fused, top_k=top_k)
            logger.debug("Reranker returned %d results", len(results))
        else:
            results = fused[:top_k]
            logger.debug("No reranker — returning top %d from fusion", len(results))

        return results

    def search_faiss_only(self, query: str, top_k: int | None = None) -> list[dict]:
        """FAISS-only search (fallback / evaluation baseline)."""
        return embedding_service.search(query, k=top_k or settings.top_k)

    def search_bm25_only(self, query: str, top_k: int | None = None) -> list[dict]:
        """BM25-only search (evaluation baseline)."""
        return bm25_service.search(query, k=top_k or settings.top_k)


hybrid_retriever = HybridRetriever()
