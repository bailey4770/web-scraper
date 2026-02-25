import asyncio
import logging

import typer

from .crawl import crawl_site_async

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.WARNING)

DEFAULT_MAX_CONCURRENCY = 10
DEFAULT_MAX_PAGES = 10
app = typer.Typer()


@app.command()
def crawl(
    base_url: str,
    max_concurrency: int = DEFAULT_MAX_CONCURRENCY,
    max_pages: int = DEFAULT_MAX_PAGES,
):
    asyncio.run(_crawl(base_url, max_concurrency, max_pages))


async def _crawl(base_url: str, max_concurrency: int, max_pages: int):
    print(f"starting crawl of: {base_url}")
    pages = await crawl_site_async(base_url, max_concurrency, max_pages)
    print("crawl complete")

    for i, url in enumerate(pages, 1):
        print(f"{i}: {url}")


def main():
    app()


if __name__ == "__main__":
    main()
