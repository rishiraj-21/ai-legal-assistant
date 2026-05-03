import json
import logging
from pathlib import Path

from app.retrieval.hybrid_retriever import hybrid_retriever

logger = logging.getLogger(__name__)

EVAL_DATASET_PATH = Path(__file__).parent / "eval_dataset.json"


def load_eval_dataset() -> list[dict]:
    with open(EVAL_DATASET_PATH, "r", encoding="utf-8") as f:
        return json.load(f)


def _is_relevant(doc: dict, expected_keywords: list[str], threshold: int = 2) -> bool:
    """A document is relevant if it contains at least `threshold` expected keywords."""
    text = doc.get("text", "").lower()
    meta = doc.get("metadata", {})
    # Also check metadata fields
    meta_text = " ".join(str(v) for v in meta.values()).lower()
    combined = text + " " + meta_text

    matches = sum(1 for kw in expected_keywords if kw.lower() in combined)
    return matches >= threshold


def recall_at_k(results: list[dict], expected_keywords: list[str], k: int = 5) -> float:
    """Fraction of expected keywords covered by top-k results."""
    top_k = results[:k]
    if not expected_keywords:
        return 0.0

    all_text = " ".join(
        doc.get("text", "").lower() + " " + " ".join(str(v) for v in doc.get("metadata", {}).values()).lower()
        for doc in top_k
    )

    found = sum(1 for kw in expected_keywords if kw.lower() in all_text)
    return found / len(expected_keywords)


def precision_at_k(results: list[dict], expected_keywords: list[str], k: int = 5) -> float:
    """Fraction of top-k results that are relevant."""
    top_k = results[:k]
    if not top_k:
        return 0.0

    relevant_count = sum(1 for doc in top_k if _is_relevant(doc, expected_keywords))
    return relevant_count / len(top_k)


def mrr(results: list[dict], expected_keywords: list[str]) -> float:
    """Mean Reciprocal Rank — rank of first relevant document."""
    for i, doc in enumerate(results):
        if _is_relevant(doc, expected_keywords):
            return 1.0 / (i + 1)
    return 0.0


def evaluate(
    method: str = "hybrid",
    k: int = 5,
) -> dict:
    """
    Evaluate retrieval quality across the eval dataset.
    method: "hybrid" | "faiss_only" | "bm25_only"
    Returns aggregate metrics.
    """
    dataset = load_eval_dataset()

    search_fn = {
        "hybrid": hybrid_retriever.search,
        "faiss_only": hybrid_retriever.search_faiss_only,
        "bm25_only": hybrid_retriever.search_bm25_only,
    }.get(method, hybrid_retriever.search)

    recalls = []
    precisions = []
    mrrs = []

    for item in dataset:
        query = item["query"]
        expected = item["expected_keywords"]

        results = search_fn(query, top_k=k)

        r = recall_at_k(results, expected, k)
        p = precision_at_k(results, expected, k)
        m = mrr(results, expected)

        recalls.append(r)
        precisions.append(p)
        mrrs.append(m)

    n = len(dataset)
    metrics = {
        "method": method,
        "k": k,
        "num_queries": n,
        "recall_at_k": round(sum(recalls) / n, 4) if n else 0,
        "precision_at_k": round(sum(precisions) / n, 4) if n else 0,
        "mrr": round(sum(mrrs) / n, 4) if n else 0,
    }

    logger.info("Evaluation [%s]: recall@%d=%.4f, precision@%d=%.4f, MRR=%.4f",
                method, k, metrics["recall_at_k"], k, metrics["precision_at_k"], metrics["mrr"])
    return metrics


def compare_all(k: int = 5) -> list[dict]:
    """Compare all retrieval methods side by side."""
    results = []
    for method in ["faiss_only", "bm25_only", "hybrid"]:
        try:
            metrics = evaluate(method=method, k=k)
            results.append(metrics)
        except Exception as e:
            logger.error("Evaluation failed for %s: %s", method, e)
            results.append({"method": method, "error": str(e)})
    return results
