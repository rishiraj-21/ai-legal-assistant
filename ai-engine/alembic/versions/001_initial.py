"""Initial schema: legal_documents, sections, cases, crawl_runs

Revision ID: 001
Revises:
Create Date: 2026-05-03
"""
from typing import Sequence, Union

from alembic import op
import sqlalchemy as sa
from sqlalchemy.dialects.postgresql import UUID, JSONB, ARRAY

revision: str = "001"
down_revision: Union[str, None] = None
branch_labels: Union[str, Sequence[str], None] = None
depends_on: Union[str, Sequence[str], None] = None


def upgrade() -> None:
    op.create_table(
        "legal_documents",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("source_type", sa.String(50), nullable=False),
        sa.Column("title", sa.String(500), nullable=False),
        sa.Column("source_url", sa.String(2000), nullable=True),
        sa.Column("source_site", sa.String(100), nullable=True),
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("category", sa.String(100), nullable=True),
        sa.Column("raw_text", sa.Text, nullable=False),
        sa.Column("content_hash", sa.String(64), nullable=False, unique=True),
        sa.Column("created_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("updated_at", sa.DateTime, server_default=sa.func.now()),
    )

    op.create_table(
        "sections",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("act_name", sa.String(500), nullable=True),
        sa.Column("section_number", sa.String(50), nullable=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False, server_default="0"),
        sa.Column("token_count", sa.Integer, nullable=True),
        sa.Column("faiss_index_id", sa.Integer, nullable=True),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_section_doc_chunk"),
    )

    op.create_table(
        "cases",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("document_id", UUID(as_uuid=True), sa.ForeignKey("legal_documents.id", ondelete="CASCADE"), nullable=False),
        sa.Column("case_name", sa.String(500), nullable=True),
        sa.Column("court", sa.String(200), nullable=True),
        sa.Column("year", sa.Integer, nullable=True),
        sa.Column("citations", ARRAY(sa.String), nullable=True),
        sa.Column("text", sa.Text, nullable=False),
        sa.Column("chunk_index", sa.Integer, nullable=False, server_default="0"),
        sa.Column("faiss_index_id", sa.Integer, nullable=True),
        sa.UniqueConstraint("document_id", "chunk_index", name="uq_case_doc_chunk"),
    )

    op.create_table(
        "crawl_runs",
        sa.Column("id", UUID(as_uuid=True), primary_key=True),
        sa.Column("source_site", sa.String(100), nullable=False),
        sa.Column("status", sa.String(50), nullable=False, server_default="running"),
        sa.Column("documents_found", sa.Integer, server_default="0"),
        sa.Column("documents_new", sa.Integer, server_default="0"),
        sa.Column("chunks_created", sa.Integer, server_default="0"),
        sa.Column("errors", JSONB, server_default="[]"),
        sa.Column("started_at", sa.DateTime, server_default=sa.func.now()),
        sa.Column("finished_at", sa.DateTime, nullable=True),
    )


def downgrade() -> None:
    op.drop_table("crawl_runs")
    op.drop_table("cases")
    op.drop_table("sections")
    op.drop_table("legal_documents")
