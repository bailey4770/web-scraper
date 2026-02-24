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
        self.semaphore: asyncio.Semaphore = asyncio.Semaphore(max_concurrency)
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

    async def _crawl_page(self, current_url: str) -> None:
        """Recursively crawl a page and all outgoing links within the same domain.

        Pages outside base_url are ignored. Already-visited pages are skipped.
        Failed fetches are recorded as None in the pages dict.

        Args:
            base_url: Root URL of the site being crawled. Only URLs starting with
                this are followed.
            current_url: URL of the page to crawl.
            pages: Accumulator dict mapping normalized URLs to their extracted data.

        Returns:
            Updated pages dict with current_url and all discovered pages added.
        """
        if not current_url.startswith(self.base_url):
            return

        normalized = normalize_url(current_url)
        if await self._add_page_visit(normalized):
            return

        async with self.semaphore:
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

        tasks = [
            asyncio.create_task(self._crawl_page(link))
            for link in data["outgoing_links"]
        ]
        _ = await asyncio.gather(*tasks)

        return

    async def crawl(self) -> Pages:
        await self._crawl_page(self.base_url)
        return self.pages


async def crawl_site_async(base_url: str, max_concurrency: int):
    async with AsyncCrawler(
        base_url,
        max_concurrency,
    ) as a:
        return await a.crawl()
