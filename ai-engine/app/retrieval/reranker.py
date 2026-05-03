import logging

from sentence_transformers import CrossEncoder

from config import settings

logger = logging.getLogger(__name__)


class Reranker:
    def __init__(self):
        self._model: CrossEncoder | None = None

    @property
    def is_loaded(self) -> bool:
        return self._model is not None

    def load(self):
        """Load the cross-encoder model."""
        if self._model is not None:
            return
        logger.info("Loading reranker model: %s", settings.reranker_model)
        self._model = CrossEncoder(settings.reranker_model)
        logger.info("Reranker model loaded.")

    def rerank(
        self, query: str, documents: list[dict], top_k: int | None = None
    ) -> list[dict]:
        """
        Re-rank documents using cross-encoder.
        Each doc must have a 'text' key.
        Returns top_k documents sorted by cross-encoder score descending.
        """
        if not self.is_loaded:
            logger.warning("Reranker not loaded — returning documents as-is.")
            return documents[:top_k] if top_k else documents

        if not documents:
            return []

        top_k = top_k or settings.reranker_top_k

        # Build (query, doc_text) pairs
        pairs = [(query, doc["text"]) for doc in documents]
        scores = self._model.predict(pairs)

        # Attach scores and sort
        scored_docs = []
        for doc, score in zip(documents, scores):
            scored_doc = dict(doc)
            scored_doc["reranker_score"] = float(score)
            scored_docs.append(scored_doc)

        scored_docs.sort(key=lambda d: d["reranker_score"], reverse=True)
        return scored_docs[:top_k]


reranker = Reranker()
