import logging
import os
import pickle
from pathlib import Path

import faiss
import numpy as np
from sentence_transformers import SentenceTransformer

from app.data.loader import load_legal_dataset
from config import settings

logger = logging.getLogger(__name__)


class EmbeddingService:
    def __init__(self):
        self.model: SentenceTransformer | None = None
        self.index: faiss.IndexFlatL2 | None = None
        self.documents: list[dict] = []
        self._dimension = 384  # all-MiniLM-L6-v2 output dim

    @property
    def index_size(self) -> int:
        return self.index.ntotal if self.index else 0

    def _load_model(self):
        if self.model is None:
            logger.info("Loading embedding model: %s", settings.embedding_model)
            self.model = SentenceTransformer(settings.embedding_model)
            logger.info("Embedding model loaded.")

    def embed(self, text: str) -> np.ndarray:
        self._load_model()
        return self.model.encode(text, normalize_embeddings=True)

    def embed_batch(self, texts: list[str]) -> np.ndarray:
        self._load_model()
        return self.model.encode(texts, normalize_embeddings=True, show_progress_bar=True)

    def build_index(self, documents: list[dict]) -> faiss.IndexFlatL2:
        texts = [doc["text"] for doc in documents]
        embeddings = self.embed_batch(texts)

        index = faiss.IndexFlatL2(self._dimension)
        index.add(embeddings.astype(np.float32))

        self.index = index
        self.documents = documents
        return index

    def search(self, query: str, k: int | None = None) -> list[dict]:
        if self.index is None or not self.documents:
            logger.warning("FAISS index not loaded — returning empty results.")
            return []

        k = min(k or settings.top_k, self.index.ntotal)
        query_vec = self.embed(query).reshape(1, -1).astype(np.float32)
        distances, indices = self.index.search(query_vec, k)

        results = []
        for i, idx in enumerate(indices[0]):
            if idx < 0 or idx >= len(self.documents):
                continue
            doc = self.documents[idx]
            results.append({
                "text": doc["text"],
                "metadata": doc["metadata"],
                "source": doc.get("source", ""),
                "score": float(distances[0][i]),
            })
        return results

    def save(self):
        store_path = Path(settings.faiss_store_path)
        store_path.mkdir(parents=True, exist_ok=True)

        index_file = store_path / "index.faiss"
        meta_file = store_path / "metadata.pkl"

        # Atomic save: write to .tmp then rename
        index_tmp = store_path / "index.faiss.tmp"
        meta_tmp = store_path / "metadata.pkl.tmp"

        faiss.write_index(self.index, str(index_tmp))
        with open(meta_tmp, "wb") as f:
            pickle.dump(self.documents, f)

        index_tmp.replace(index_file)
        meta_tmp.replace(meta_file)
        logger.info("FAISS index saved to %s (%d vectors)", store_path, self.index_size)

    def load(self) -> bool:
        store_path = Path(settings.faiss_store_path)
        index_file = store_path / "index.faiss"
        meta_file = store_path / "metadata.pkl"

        if not index_file.exists() or not meta_file.exists():
            return False

        self.index = faiss.read_index(str(index_file))
        with open(meta_file, "rb") as f:
            self.documents = pickle.load(f)
        logger.info("FAISS index loaded from disk (%d vectors)", self.index_size)
        return True

    def load_or_build(self):
        if self.load():
            return

        logger.info("No existing index found — building from legal dataset...")
        docs = load_legal_dataset(settings.legal_dataset_path)
        if not docs:
            logger.warning("No legal documents found. FAISS index will be empty.")
            self.index = faiss.IndexFlatL2(self._dimension)
            self.documents = []
            return

        self.build_index(docs)
        self.save()


    async def rebuild_from_db(self):
        """Rebuild FAISS index from all chunks in PostgreSQL."""
        from app.db.database import get_session
        from app.db.repository import get_all_chunks

        logger.info("Rebuilding FAISS index from database...")
        async with get_session() as session:
            chunks = await get_all_chunks(session)

        if not chunks:
            logger.warning("No chunks found in database. FAISS index will be empty.")
            self.index = faiss.IndexFlatL2(self._dimension)
            self.documents = []
            self.save()
            return

        self.build_index(chunks)
        self.save()
        logger.info("FAISS index rebuilt from DB: %d vectors", self.index_size)


embedding_service = EmbeddingService()
