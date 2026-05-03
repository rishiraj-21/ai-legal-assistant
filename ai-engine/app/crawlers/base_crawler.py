import asyncio
import logging
from abc import ABC, abstractmethod

import httpx

from config import settings

logger = logging.getLogger(__name__)


class BaseCrawler(ABC):
    """Async HTTP crawler with rate limiting and exponential backoff."""

    def __init__(self):
        self.delay = settings.crawler_delay_seconds
        self.max_retries = settings.crawler_max_retries
        self.backoff_base = settings.crawler_backoff_base
        self._client: httpx.AsyncClient | None = None

    async def _get_client(self) -> httpx.AsyncClient:
        if self._client is None or self._client.is_closed:
            self._client = httpx.AsyncClient(
                timeout=httpx.Timeout(30.0, connect=10.0),
                headers={
                    "User-Agent": settings.crawler_user_agent,
                    "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
                    "Accept-Language": "en-US,en;q=0.5",
                },
                follow_redirects=True,
                limits=httpx.Limits(max_connections=5, max_keepalive_connections=2),
            )
        return self._client

    async def fetch(self, url: str) -> str | None:
        """Fetch a URL with rate limiting and retry logic."""
        client = await self._get_client()

        for attempt in range(self.max_retries):
            try:
                await asyncio.sleep(self.delay)
                response = await client.get(url)
                response.raise_for_status()
                return response.text
            except httpx.HTTPStatusError as e:
                status = e.response.status_code
                if status == 429 or status >= 500:
                    wait = self.backoff_base ** (attempt + 1)
                    logger.warning(
                        "Retryable HTTP %d for %s, retry %d/%d in %.1fs",
                        status, url, attempt + 1, self.max_retries, wait,
                    )
                    await asyncio.sleep(wait)
                else:
                    logger.error("HTTP %d for %s — not retryable", status, url)
                    return None
            except (httpx.ConnectError, httpx.ReadTimeout) as e:
                wait = self.backoff_base ** (attempt + 1)
                logger.warning(
                    "Connection error for %s (%s), retry %d/%d in %.1fs",
                    url, type(e).__name__, attempt + 1, self.max_retries, wait,
                )
                await asyncio.sleep(wait)
            except Exception as e:
                logger.error("Unexpected error fetching %s: %s", url, e)
                return None

        logger.error("All retries exhausted for %s", url)
        return None

    async def close(self):
        if self._client and not self._client.is_closed:
            await self._client.aclose()
            self._client = None

    @abstractmethod
    async def crawl(self) -> list[dict]:
        """
        Run the crawl and return list of raw documents.
        Each dict: {"title": str, "text": str, "source_url": str, "source_type": str, "metadata": dict}
        """
        ...

    @property
    @abstractmethod
    def source_site(self) -> str:
        ...
