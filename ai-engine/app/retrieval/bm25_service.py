import logging
import os
import pickle
from pathlib import Path

from rank_bm25 import BM25Okapi

from config import settings

logger = logging.getLogger(__name__)


class BM25Service:
    def __init__(self):
        self.bm25: BM25Okapi | None = None
        self.documents: list[dict] = []
        self._tokenized_corpus: list[list[str]] = []

    @property
    def is_loaded(self) -> bool:
        return self.bm25 is not None and len(self.documents) > 0

    @property
    def index_size(self) -> int:
        return len(self.documents)

    def _tokenize(self, text: str) -> list[str]:
        """Simple whitespace + lowercased tokenization for BM25."""
        return text.lower().split()

    def build(self, documents: list[dict]):
        """Build BM25 index from a list of document dicts with 'text' key."""
        self._tokenized_corpus = [self._tokenize(doc["text"]) for doc in documents]
        self.bm25 = BM25Okapi(self._tokenized_corpus)
        self.documents = documents
        logger.info("BM25 index built with %d documents", len(documents))

    def search(self, query: str, k: int | None = None) -> list[dict]:
        """Return top-k documents ranked by BM25 score."""
        if not self.is_loaded:
            logger.warning("BM25 index not loaded — returning empty results.")
            return []

        k = min(k or settings.top_k, len(self.documents))
        tokenized_query = self._tokenize(query)
        scores = self.bm25.get_scores(tokenized_query)

        # Get top-k indices by score (descending)
        top_indices = sorted(range(len(scores)), key=lambda i: scores[i], reverse=True)[:k]

        results = []
        for idx in top_indices:
            doc = self.documents[idx]
            results.append({
                "text": doc["text"],
                "metadata": doc.get("metadata", {}),
                "source": doc.get("source", ""),
                "score": float(scores[idx]),
                "rank": len(results),
            })
        return results

    def save(self):
        """Save BM25 index and documents to disk."""
        store_path = Path(settings.bm25_store_path)
        store_path.mkdir(parents=True, exist_ok=True)

        bm25_file = store_path / "bm25.pkl"
        docs_file = store_path / "bm25_docs.pkl"

        # Atomic save: write to .tmp then rename
        bm25_tmp = store_path / "bm25.pkl.tmp"
        docs_tmp = store_path / "bm25_docs.pkl.tmp"

        with open(bm25_tmp, "wb") as f:
            pickle.dump(self.bm25, f)
        with open(docs_tmp, "wb") as f:
            pickle.dump(self.documents, f)

        # Atomic rename
        bm25_tmp.replace(bm25_file)
        docs_tmp.replace(docs_file)

        logger.info("BM25 index saved to %s (%d documents)", store_path, len(self.documents))

    def load(self) -> bool:
        """Load BM25 index from disk. Returns True if successful."""
        store_path = Path(settings.bm25_store_path)
        bm25_file = store_path / "bm25.pkl"
        docs_file = store_path / "bm25_docs.pkl"

        if not bm25_file.exists() or not docs_file.exists():
            return False

        try:
            with open(bm25_file, "rb") as f:
                self.bm25 = pickle.load(f)
            with open(docs_file, "rb") as f:
                self.documents = pickle.load(f)
            logger.info("BM25 index loaded from disk (%d documents)", len(self.documents))
            return True
        except Exception as e:
            logger.error("Failed to load BM25 index: %s", e)
            return False


bm25_service = BM25Service()
