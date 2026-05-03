import logging

from fastapi import APIRouter, HTTPException, Query

from app.crawlers.crawl_manager import ingest_seed_data, run_crawl
from app.db.database import get_session
from app.db.repository import get_chunk_count, get_recent_crawl_runs
from app.evaluation.evaluator import compare_all, evaluate
from app.scheduler.jobs import rebuild_indexes_job

logger = logging.getLogger(__name__)
router = APIRouter(prefix="/admin", tags=["admin"])


@router.post("/crawl")
async def trigger_crawl(source: str = Query(..., description="Source to crawl: indiacode or indiankanoon")):
    """Trigger a crawl for the specified source."""
    try:
        stats = await run_crawl(source)
        return {"status": "completed", **stats}
    except ValueError as e:
        raise HTTPException(status_code=400, detail=str(e))
    except Exception as e:
        logger.error("Crawl trigger failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Crawl failed: {e}")


@router.post("/ingest-seed")
async def trigger_seed_ingest():
    """Ingest seed .txt files into the database."""
    try:
        result = await ingest_seed_data()
        return {"status": "completed", **result}
    except Exception as e:
        logger.error("Seed ingest failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Seed ingest failed: {e}")


@router.post("/rebuild-index")
async def trigger_rebuild_index():
    """Rebuild FAISS and BM25 indexes from the database."""
    try:
        await rebuild_indexes_job()
        return {"status": "completed", "message": "Indexes rebuilt successfully."}
    except Exception as e:
        logger.error("Index rebuild failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Rebuild failed: {e}")


@router.get("/crawl-history")
async def crawl_history(limit: int = Query(10, ge=1, le=100)):
    """Get recent crawl run history."""
    async with get_session() as session:
        runs = await get_recent_crawl_runs(session, limit=limit)
        return [
            {
                "id": str(r.id),
                "source_site": r.source_site,
                "status": r.status,
                "documents_found": r.documents_found,
                "documents_new": r.documents_new,
                "chunks_created": r.chunks_created,
                "errors": r.errors,
                "started_at": r.started_at.isoformat() if r.started_at else None,
                "finished_at": r.finished_at.isoformat() if r.finished_at else None,
            }
            for r in runs
        ]


@router.get("/stats")
async def db_stats():
    """Get database statistics."""
    async with get_session() as session:
        chunks = await get_chunk_count(session)
    return {"total_chunks": chunks}


@router.post("/evaluate")
async def trigger_evaluation(
    method: str = Query("hybrid", description="Retrieval method: hybrid, faiss_only, bm25_only"),
    k: int = Query(5, ge=1, le=20),
):
    """Run retrieval evaluation."""
    try:
        metrics = evaluate(method=method, k=k)
        return metrics
    except Exception as e:
        logger.error("Evaluation failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Evaluation failed: {e}")


@router.post("/evaluate/compare")
async def trigger_comparison(k: int = Query(5, ge=1, le=20)):
    """Compare all retrieval methods."""
    try:
        results = compare_all(k=k)
        return {"comparisons": results}
    except Exception as e:
        logger.error("Comparison failed: %s", e)
        raise HTTPException(status_code=500, detail=f"Comparison failed: {e}")
