import asyncio
import logging

import typer

from .crawl import crawl_site_async

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

DEFAULT_MAX_CONCURRENCY = 4
app = typer.Typer()


@app.command()
def crawl(base_url: str, max_concurrency: int = DEFAULT_MAX_CONCURRENCY):
    asyncio.run(_crawl(base_url, max_concurrency))


async def _crawl(base_url: str, max_concurrency: int):
    print(f"starting crawl of: {base_url}")
    pages = await crawl_site_async(base_url, max_concurrency)
    print("crawl complete")
    i = 1
    for url, data in pages.items():
        if data is None:
            continue
        print(f"{i}: {url}")
        i += 1


def main():
    app()


if __name__ == "__main__":
    main()
