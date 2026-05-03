import logging
from datetime import datetime

from app.crawlers.indiacode_crawler import IndiaCodeCrawler
from app.crawlers.indiankanoon_crawler import IndianKanoonCrawler
from app.db.database import get_session
from app.db.repository import (
    content_hash,
    create_crawl_run,
    finish_crawl_run,
    insert_case,
    insert_document,
    insert_section,
)
from app.processing.chunker import chunk_text
from app.processing.cleaner import clean_legal_text
from app.processing.metadata_extractor import extract_act_metadata, extract_case_metadata

logger = logging.getLogger(__name__)

CRAWLERS = {
    "indiacode": IndiaCodeCrawler,
    "indiankanoon": IndianKanoonCrawler,
}


async def run_crawl(source: str) -> dict:
    """
    Orchestrate: crawl → clean → chunk → store → return stats.
    Call rebuild_index separately after crawl completes.
    """
    if source not in CRAWLERS:
        raise ValueError(f"Unknown source: {source}. Available: {list(CRAWLERS.keys())}")

    crawler = CRAWLERS[source]()
    stats = {
        "source": source,
        "documents_found": 0,
        "documents_new": 0,
        "chunks_created": 0,
        "errors": [],
    }

    # Create crawl run record
    async with get_session() as session:
        crawl_run = await create_crawl_run(session, source)
        run_id = crawl_run.id

    try:
        # 1. Crawl
        logger.info("Starting crawl for source: %s", source)
        raw_docs = await crawler.crawl()
        stats["documents_found"] = len(raw_docs)
        logger.info("Crawled %d documents from %s", len(raw_docs), source)

        # 2. Process and store
        async with get_session() as session:
            for raw_doc in raw_docs:
                try:
                    # Clean
                    cleaned_text = clean_legal_text(raw_doc["text"], is_html=False)
                    if len(cleaned_text) < 50:
                        continue

                    # Insert document (dedup by content hash)
                    doc = await insert_document(
                        session,
                        source_type=raw_doc["source_type"],
                        title=raw_doc["title"],
                        raw_text=cleaned_text,
                        source_url=raw_doc.get("source_url"),
                        source_site=source,
                        year=raw_doc.get("metadata", {}).get("year"),
                        category=raw_doc.get("metadata", {}).get("category"),
                    )

                    if doc is None:
                        # Duplicate
                        continue

                    stats["documents_new"] += 1

                    # Chunk
                    chunks = chunk_text(cleaned_text)

                    # Store chunks
                    metadata = raw_doc.get("metadata", {})
                    for chunk in chunks:
                        if raw_doc["source_type"] == "case_law":
                            await insert_case(
                                session,
                                document_id=doc.id,
                                text=chunk["text"],
                                chunk_index=chunk["chunk_index"],
                                case_name=metadata.get("case_name"),
                                court=metadata.get("court"),
                                year=metadata.get("year"),
                                citations=metadata.get("citations"),
                            )
                        else:
                            await insert_section(
                                session,
                                document_id=doc.id,
                                text=chunk["text"],
                                chunk_index=chunk["chunk_index"],
                                act_name=metadata.get("act_name"),
                                section_number=metadata.get("section_number"),
                                token_count=chunk.get("token_count"),
                            )
                        stats["chunks_created"] += 1

                except Exception as e:
                    error_msg = f"Error processing doc '{raw_doc.get('title', 'unknown')}': {e}"
                    logger.error(error_msg)
                    stats["errors"].append(error_msg)

        # Update crawl run
        async with get_session() as session:
            await finish_crawl_run(
                session, run_id, "completed",
                documents_found=stats["documents_found"],
                documents_new=stats["documents_new"],
                chunks_created=stats["chunks_created"],
                errors=stats["errors"],
            )

    except Exception as e:
        logger.error("Crawl failed for %s: %s", source, e)
        stats["errors"].append(str(e))
        async with get_session() as session:
            await finish_crawl_run(session, run_id, "failed", errors=stats["errors"])

    return stats


async def run_full_crawl() -> list[dict]:
    """Run crawls for all sources."""
    results = []
    for source in CRAWLERS:
        result = await run_crawl(source)
        results.append(result)
    return results


async def ingest_seed_data():
    """Ingest the 58 seed .txt files from legal_dataset into PostgreSQL."""
    from app.data.loader import load_legal_dataset
    from config import settings

    logger.info("Ingesting seed data from %s", settings.legal_dataset_path)
    docs = load_legal_dataset(settings.legal_dataset_path)

    async with get_session() as session:
        new_count = 0
        chunk_count = 0

        for doc in docs:
            metadata = doc.get("metadata", {})
            title = f"{metadata.get('act', 'Unknown')} — Section {metadata.get('section', '?')}"

            db_doc = await insert_document(
                session,
                source_type="seed",
                title=title,
                raw_text=doc["text"],
                source_site="seed",
                category=metadata.get("category"),
            )

            if db_doc is None:
                continue

            new_count += 1

            chunks = chunk_text(doc["text"])
            for chunk in chunks:
                await insert_section(
                    session,
                    document_id=db_doc.id,
                    text=chunk["text"],
                    chunk_index=chunk["chunk_index"],
                    act_name=metadata.get("act"),
                    section_number=metadata.get("section"),
                    token_count=chunk.get("token_count"),
                )
                chunk_count += 1

    logger.info("Seed data ingested: %d new documents, %d chunks", new_count, chunk_count)
    return {"documents_new": new_count, "chunks_created": chunk_count}
