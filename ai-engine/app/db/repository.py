import hashlib
import logging
from datetime import datetime
from uuid import UUID

from sqlalchemy import select, func
from sqlalchemy.ext.asyncio import AsyncSession

from app.db.models import Case, CrawlRun, LegalDocument, Section

logger = logging.getLogger(__name__)


def content_hash(text: str) -> str:
    return hashlib.sha256(text.encode("utf-8")).hexdigest()


async def insert_document(
    session: AsyncSession,
    source_type: str,
    title: str,
    raw_text: str,
    source_url: str | None = None,
    source_site: str | None = None,
    year: int | None = None,
    category: str | None = None,
) -> LegalDocument | None:
    """Insert a document if it doesn't already exist (dedup by content_hash)."""
    hash_val = content_hash(raw_text)
    existing = await session.execute(
        select(LegalDocument).where(LegalDocument.content_hash == hash_val)
    )
    if existing.scalar_one_or_none():
        return None

    doc = LegalDocument(
        source_type=source_type,
        title=title,
        source_url=source_url,
        source_site=source_site,
        year=year,
        category=category,
        raw_text=raw_text,
        content_hash=hash_val,
    )
    session.add(doc)
    await session.flush()
    return doc


async def insert_section(
    session: AsyncSession,
    document_id: UUID,
    text: str,
    chunk_index: int,
    act_name: str | None = None,
    section_number: str | None = None,
    token_count: int | None = None,
    faiss_index_id: int | None = None,
) -> Section:
    section = Section(
        document_id=document_id,
        act_name=act_name,
        section_number=section_number,
        text=text,
        chunk_index=chunk_index,
        token_count=token_count,
        faiss_index_id=faiss_index_id,
    )
    session.add(section)
    await session.flush()
    return section


async def insert_case(
    session: AsyncSession,
    document_id: UUID,
    text: str,
    chunk_index: int,
    case_name: str | None = None,
    court: str | None = None,
    year: int | None = None,
    citations: list[str] | None = None,
    faiss_index_id: int | None = None,
) -> Case:
    case = Case(
        document_id=document_id,
        case_name=case_name,
        court=court,
        year=year,
        citations=citations,
        text=text,
        chunk_index=chunk_index,
        faiss_index_id=faiss_index_id,
    )
    session.add(case)
    await session.flush()
    return case


async def get_all_chunks(session: AsyncSession) -> list[dict]:
    """Return all chunks (sections + cases) for index building."""
    chunks = []

    sections = await session.execute(select(Section))
    for s in sections.scalars().all():
        chunks.append({
            "id": str(s.id),
            "text": s.text,
            "metadata": {
                "type": "section",
                "act": s.act_name or "",
                "section": s.section_number or "",
                "document_id": str(s.document_id),
            },
            "source": s.act_name or "unknown",
        })

    cases = await session.execute(select(Case))
    for c in cases.scalars().all():
        chunks.append({
            "id": str(c.id),
            "text": c.text,
            "metadata": {
                "type": "case",
                "case_name": c.case_name or "",
                "court": c.court or "",
                "year": c.year,
                "document_id": str(c.document_id),
            },
            "source": c.case_name or "unknown",
        })

    return chunks


async def get_chunk_count(session: AsyncSession) -> int:
    sec_count = await session.execute(select(func.count(Section.id)))
    case_count = await session.execute(select(func.count(Case.id)))
    return sec_count.scalar() + case_count.scalar()


async def create_crawl_run(
    session: AsyncSession, source_site: str
) -> CrawlRun:
    run = CrawlRun(source_site=source_site, status="running")
    session.add(run)
    await session.flush()
    return run


async def finish_crawl_run(
    session: AsyncSession,
    run_id: UUID,
    status: str,
    documents_found: int = 0,
    documents_new: int = 0,
    chunks_created: int = 0,
    errors: list | None = None,
):
    run = await session.get(CrawlRun, run_id)
    if run:
        run.status = status
        run.documents_found = documents_found
        run.documents_new = documents_new
        run.chunks_created = chunks_created
        run.errors = errors or []
        run.finished_at = datetime.utcnow()
        await session.flush()


async def get_recent_crawl_runs(
    session: AsyncSession, limit: int = 10
) -> list[CrawlRun]:
    result = await session.execute(
        select(CrawlRun).order_by(CrawlRun.started_at.desc()).limit(limit)
    )
    return list(result.scalars().all())
