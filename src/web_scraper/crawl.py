import requests
import logging

from .html_parse import PageData, extract_page_data, normalize_url

logger = logging.getLogger(__name__)


def crawl_page(
    base_url: str, current_url: str, pages: dict[str, PageData | None]
) -> dict[str, PageData | None]:
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
    if not current_url.startswith(base_url):
        return pages

    normalized = normalize_url(current_url)
    if normalized in pages.keys():
        return pages

    logger.info("Scraping data from %s", current_url)
    try:
        html = get_html(current_url)
    except Exception as e:
        logger.warning("failed to fetch %s: %s", current_url, e)
        pages[normalized] = None
        return pages

    data = extract_page_data(html, current_url)
    pages[normalized] = data
    logger.info("scraped data from %s", current_url)
    logger.debug("scraped data: %s", data)

    for link in data["outgoing_links"]:
        pages = crawl_page(base_url, link, pages)

    return pages


def get_html(url: str):
    r = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=10)
    r.raise_for_status()

    if "text/html" not in r.headers.get("content-type", ""):
        raise ValueError(
            f"expected text/html, got {r.headers.get('content-type')} for url: {r.url}"
        )

    return r.text
