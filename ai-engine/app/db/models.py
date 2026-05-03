import uuid
from datetime import datetime

from sqlalchemy import (
    Column,
    DateTime,
    ForeignKey,
    Integer,
    String,
    Text,
    UniqueConstraint,
)
from sqlalchemy.dialects.postgresql import ARRAY, JSONB, UUID
from sqlalchemy.orm import DeclarativeBase, relationship


class Base(DeclarativeBase):
    pass


class LegalDocument(Base):
    __tablename__ = "legal_documents"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_type = Column(String(50), nullable=False)  # statute | case_law | seed
    title = Column(String(500), nullable=False)
    source_url = Column(String(2000), nullable=True)
    source_site = Column(String(100), nullable=True)  # indiacode | indiankanoon | seed
    year = Column(Integer, nullable=True)
    category = Column(String(100), nullable=True)
    raw_text = Column(Text, nullable=False)
    content_hash = Column(String(64), nullable=False, unique=True)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    sections = relationship("Section", back_populates="document", cascade="all, delete-orphan")
    cases = relationship("Case", back_populates="document", cascade="all, delete-orphan")


class Section(Base):
    __tablename__ = "sections"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False)
    act_name = Column(String(500), nullable=True)
    section_number = Column(String(50), nullable=True)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False, default=0)
    token_count = Column(Integer, nullable=True)
    faiss_index_id = Column(Integer, nullable=True)

    document = relationship("LegalDocument", back_populates="sections")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_section_doc_chunk"),
    )


class Case(Base):
    __tablename__ = "cases"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    document_id = Column(UUID(as_uuid=True), ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False)
    case_name = Column(String(500), nullable=True)
    court = Column(String(200), nullable=True)
    year = Column(Integer, nullable=True)
    citations = Column(ARRAY(String), nullable=True)
    text = Column(Text, nullable=False)
    chunk_index = Column(Integer, nullable=False, default=0)
    faiss_index_id = Column(Integer, nullable=True)

    document = relationship("LegalDocument", back_populates="cases")

    __table_args__ = (
        UniqueConstraint("document_id", "chunk_index", name="uq_case_doc_chunk"),
    )


class CrawlRun(Base):
    __tablename__ = "crawl_runs"

    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    source_site = Column(String(100), nullable=False)
    status = Column(String(50), nullable=False, default="running")  # running | completed | failed
    documents_found = Column(Integer, default=0)
    documents_new = Column(Integer, default=0)
    chunks_created = Column(Integer, default=0)
    errors = Column(JSONB, default=list)
    started_at = Column(DateTime, default=datetime.utcnow)
    finished_at = Column(DateTime, nullable=True)
