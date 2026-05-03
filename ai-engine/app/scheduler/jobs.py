import asyncio
import logging

from apscheduler.schedulers.asyncio import AsyncIOScheduler
from apscheduler.triggers.cron import CronTrigger

from config import settings

logger = logging.getLogger(__name__)

scheduler = AsyncIOScheduler()


async def weekly_crawl_job():
    """Crawl all sources and rebuild indexes."""
    from app.crawlers.crawl_manager import run_full_crawl
    logger.info("Scheduled weekly crawl starting...")
    try:
        results = await run_full_crawl()
        total_new = sum(r.get("documents_new", 0) for r in results)
        total_chunks = sum(r.get("chunks_created", 0) for r in results)
        logger.info("Weekly crawl complete: %d new docs, %d chunks", total_new, total_chunks)

        if total_new > 0:
            await rebuild_indexes_job()
    except Exception as e:
        logger.error("Weekly crawl failed: %s", e)


async def rebuild_indexes_job():
    """Rebuild FAISS and BM25 indexes from database."""
    from app.retrieval.bm25_service import bm25_service
    from app.services.embedding_service import embedding_service
    from app.db.database import get_session
    from app.db.repository import get_all_chunks

    logger.info("Scheduled index rebuild starting...")
    try:
        # Get all chunks from DB
        async with get_session() as session:
            chunks = await get_all_chunks(session)

        if not chunks:
            logger.warning("No chunks in DB — skipping rebuild.")
            return

        # Rebuild FAISS
        await embedding_service.rebuild_from_db()

        # Rebuild BM25
        bm25_service.build(chunks)
        bm25_service.save()

        logger.info("Index rebuild complete: %d chunks indexed", len(chunks))
    except Exception as e:
        logger.error("Index rebuild failed: %s", e)


def start_scheduler():
    """Configure and start the APScheduler."""
    # Weekly crawl: Sunday at 2 AM
    scheduler.add_job(
        weekly_crawl_job,
        trigger=CronTrigger(
            day_of_week=settings.crawl_cron_day_of_week,
            hour=settings.crawl_cron_hour,
        ),
        id="weekly_crawl",
        name="Weekly Legal Data Crawl",
        replace_existing=True,
    )

    # Mid-week index rebuild: Wednesday at 3 AM
    scheduler.add_job(
        rebuild_indexes_job,
        trigger=CronTrigger(
            day_of_week=settings.rebuild_cron_day_of_week,
            hour=settings.rebuild_cron_hour,
        ),
        id="midweek_rebuild",
        name="Mid-week Index Rebuild",
        replace_existing=True,
    )

    scheduler.start()
    logger.info("Scheduler started: weekly crawl (%s %d:00), rebuild (%s %d:00)",
                settings.crawl_cron_day_of_week, settings.crawl_cron_hour,
                settings.rebuild_cron_day_of_week, settings.rebuild_cron_hour)


def stop_scheduler():
    if scheduler.running:
        scheduler.shutdown(wait=False)
        logger.info("Scheduler stopped.")
