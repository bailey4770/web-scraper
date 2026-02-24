import logging

import typer

from .crawl import crawl_page

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

app = typer.Typer()


@app.command()
def crawl(base_url: str):
    print(f"starting crawl of: {base_url}")
    pages = crawl_page(base_url, base_url, {})
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
