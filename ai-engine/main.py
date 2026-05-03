import json
import logging
import uuid
from contextvars import ContextVar
from contextlib import asynccontextmanager
from datetime import datetime, timezone

from fastapi import FastAPI, Request, Response
from fastapi.middleware.cors import CORSMiddleware
from starlette.middleware.base import BaseHTTPMiddleware

from app.db.database import check_connection, dispose_engine
from app.retrieval.bm25_service import bm25_service
from app.retrieval.reranker import reranker
from app.routers import admin, analysis, health
from app.scheduler.jobs import start_scheduler, stop_scheduler
from app.services.embedding_service import embedding_service

# ── Correlation ID context var ────────────────────────────────
correlation_id_var: ContextVar[str] = ContextVar("correlation_id", default="")


# ── JSON log formatter ───────────────────────────────────────
class JsonFormatter(logging.Formatter):
    def format(self, record: logging.LogRecord) -> str:
        log_entry = {
            "timestamp": datetime.now(timezone.utc).isoformat(),
            "level": record.levelname,
            "logger": record.name,
            "message": record.getMessage(),
            "correlation_id": correlation_id_var.get(""),
        }
        if record.exc_info and record.exc_info[0] is not None:
            log_entry["exception"] = self.formatException(record.exc_info)
        return json.dumps(log_entry)


# Configure root logger with JSON formatter
handler = logging.StreamHandler()
handler.setFormatter(JsonFormatter())
logging.root.handlers = [handler]
logging.root.setLevel(logging.INFO)

logger = logging.getLogger(__name__)


# ── Correlation ID middleware ─────────────────────────────────
class CorrelationIdMiddleware(BaseHTTPMiddleware):
    async def dispatch(self, request: Request, call_next) -> Response:
        corr_id = request.headers.get("x-correlation-id") or uuid.uuid4().hex[:12]
        correlation_id_var.set(corr_id)
        response = await call_next(request)
        response.headers["X-Correlation-Id"] = corr_id
        return response


@asynccontextmanager
async def lifespan(app: FastAPI):
    # 1. Load FAISS index (from disk or build from seed files)
    logger.info("Starting up — loading FAISS index...")
    embedding_service.load_or_build()
    logger.info("FAISS index ready (%d vectors)", embedding_service.index_size)

    # 2. Load BM25 index (if previously built)
    if bm25_service.load():
        logger.info("BM25 index ready (%d documents)", bm25_service.index_size)
    else:
        logger.info("No BM25 index found — build via POST /admin/rebuild-index")

    # 3. Load reranker model
    try:
        reranker.load()
        logger.info("Reranker model loaded.")
    except Exception as e:
        logger.warning("Reranker failed to load (non-critical): %s", e)

    # 4. Check DB connection
    db_ok = await check_connection()
    if db_ok:
        logger.info("Database connection verified.")
    else:
        logger.warning("Database not available — crawl/admin features will not work.")

    # 5. Start scheduler
    try:
        start_scheduler()
    except Exception as e:
        logger.warning("Scheduler failed to start: %s", e)

    yield

    # Shutdown
    stop_scheduler()
    await dispose_engine()
    logger.info("Shutting down.")


app = FastAPI(title="AI Legal Engine", version="2.0.0", lifespan=lifespan)

app.add_middleware(CorrelationIdMiddleware)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:5058",
        "http://localhost:7235",
        "http://localhost:4200",
        "http://localhost:4000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
    expose_headers=["X-Correlation-Id"],
)

app.include_router(health.router)
app.include_router(analysis.router)
app.include_router(admin.router)
