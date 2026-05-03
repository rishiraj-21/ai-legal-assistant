from fastapi import APIRouter

from app.db.database import check_connection
from app.retrieval.bm25_service import bm25_service
from app.retrieval.reranker import reranker
from app.services.embedding_service import embedding_service

router = APIRouter()


@router.get("/health")
async def health_check():
    db_connected = await check_connection()

    return {
        "status": "ok",
        "faiss_loaded": embedding_service.index is not None,
        "index_size": embedding_service.index_size,
        "bm25_loaded": bm25_service.is_loaded,
        "bm25_size": bm25_service.index_size,
        "reranker_loaded": reranker.is_loaded,
        "db_connected": db_connected,
    }
