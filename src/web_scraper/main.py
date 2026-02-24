import logging
import sys

import requests
import typer

from .fetch import get_html

logger = logging.getLogger(__name__)

app = typer.Typer()


@app.command()
def crawl(base_url: str):
    print(f"starting crawl of: {base_url}")

    try:
        html = get_html(base_url)
    except requests.exceptions.Timeout:
        logger.warning("timeout fetching %s", base_url)
        sys.exit(1)
    except requests.exceptions.ConnectionError:
        logger.warning("connection error fetching %s, skipping", base_url)
        sys.exit(1)
    except requests.exceptions.HTTPError as e:
        logger.warning("http error %s fetching %s, skipping", e, base_url)
        sys.exit(1)

    print(html)


def main():
    app()


if __name__ == "__main__":
    main()
