import asyncio
import logging
from types import TracebackType
from typing import Self, TypeAlias

import aiohttp

from .html_parse import PageData, extract_page_data, normalize_url

logger = logging.getLogger(__name__)

Pages: TypeAlias = dict[str, PageData | None]


class AsyncCrawler:
    def __init__(self, base_url: str, max_concurrency: int) -> None:
        self.base_url: str = base_url
        self.pages: Pages = {}
        self.lock: asyncio.Lock = asyncio.Lock()
        self.max_concurrency: int = max_concurrency
        self.session: aiohttp.ClientSession | None = None

    async def __aenter__(self) -> Self:
        self.session = aiohttp.ClientSession()
        return self

    async def __aexit__(
        self,
        exc_type: type[BaseException] | None,
        exc_val: BaseException | None,
        exc_tb: TracebackType | None,
    ) -> None:
        assert self.session is not None
        await self.session.close()

    async def _add_page_visit(self, normalized_url: str) -> bool:
        async with self.lock:
            if normalized_url in self.pages:
                return True

            self.pages[normalized_url] = None
            return False

    async def _get_html(self, url: str) -> str:
        assert self.session is not None
        async with self.session.get(
            url, headers={"User-Agent": "BootCrawler/1.0"}, raise_for_status=True
        ) as r:
            assert "text/html" in r.headers.get("content-type", "")
            return await r.text()

    async def _crawl_page(self, current_url: str, queue: asyncio.Queue[str]) -> None:
        if not current_url.startswith(self.base_url):
            return

        normalized = normalize_url(current_url)
        if await self._add_page_visit(normalized):
            return

        logger.info("Scraping data from %s", current_url)
        try:
            html = await self._get_html(current_url)
        except Exception as e:
            logger.warning("failed to fetch %s: %s", current_url, e)
            async with self.lock:
                self.pages[normalized] = None
            return

        data = extract_page_data(html, current_url)

        async with self.lock:
            self.pages[normalized] = data

        logger.info("Scraped data from %s", current_url)
        logger.debug("scraped data: %s", data)

        for link in data["outgoing_links"]:
            await queue.put(link)

    async def crawl(self) -> Pages:
        queue: asyncio.Queue[str] = asyncio.Queue()
        queue.put_nowait(self.base_url)

        async def worker():
            while True:
                url = await queue.get()
                try:
                    await self._crawl_page(url, queue)
                except Exception as e:
                    logger.warning("unhandled error crawling %s: %s", url, e)
                finally:
                    queue.task_done()

        workers = [asyncio.create_task(worker()) for _ in range(self.max_concurrency)]
        await queue.join()
        for w in workers:
            _ = w.cancel()
        return self.pages


async def crawl_site_async(base_url: str, max_concurrency: int) -> dict[str, PageData]:
    """Crawl a website asynchronously and return extracted page data.

    Args:
        base_url: URL to start crawling from. Only pages within this domain are crawled.
        max_concurrency: Maximum number of concurrent HTTP requests. Defaults to 4.

    Returns:
        Dict mapping normalized URLs to their extracted PageData.
    """
    async with AsyncCrawler(
        base_url,
        max_concurrency,
    ) as a:
        pages = await a.crawl()
        return {k: v for k, v in pages.items() if v is not None}
