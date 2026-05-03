from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Gemini
    gemini_api_key: str = ""
    model_name: str = "gemini-2.0-flash"

    # Embeddings / FAISS
    embedding_model: str = "all-MiniLM-L6-v2"
    faiss_store_path: str = "app/faiss_store"
    legal_dataset_path: str = "app/legal_dataset"
    top_k: int = 5

    # Database
    database_url: str = "postgresql+asyncpg://postgres:postgres@localhost:5432/legal_ai"

    # BM25
    bm25_store_path: str = "app/bm25_store"

    # Reranker
    reranker_model: str = "cross-encoder/ms-marco-MiniLM-L-6-v2"
    reranker_top_k: int = 5

    # Crawler
    crawler_delay_seconds: float = 3.0
    crawler_max_retries: int = 3
    crawler_backoff_base: float = 2.0
    crawler_user_agent: str = "LegalAI-Research-Bot/1.0 (+https://github.com/legal-ai)"

    # Scheduler
    crawl_cron_day_of_week: str = "sun"
    crawl_cron_hour: int = 2
    rebuild_cron_day_of_week: str = "wed"
    rebuild_cron_hour: int = 3

    # Chunking
    chunk_size_tokens: int = 512
    chunk_overlap_tokens: int = 50

    model_config = {"env_file": ".env", "env_file_encoding": "utf-8"}


settings = Settings()
