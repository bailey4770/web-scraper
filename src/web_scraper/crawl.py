import logging
from typing import TypedDict
from urllib.parse import urljoin, urlsplit

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


class PageData(TypedDict):
    url: str
    h1: str
    first_paragraph: str
    outgoing_links: list[str]
    image_urls: list[str]


def extract_page_data(html: str, page_url: str) -> PageData:
    """Extract structured data from an HTML page.

    Args:
        html: Raw HTML string to parse.
        page_url: URL of the page, included in the returned data and used to resolve relative URLs.

    Returns:
        PageData dict containing url, h1, first_paragraph, outgoing_links, and image_urls.

    Raises:
        ValueError: If html is empty.
    """
    return {
        "url": page_url,
        "h1": get_h1_from_html(html),
        "first_paragraph": get_first_paragraph_from_html(html),
        "outgoing_links": get_urls_from_html(html, page_url),
        "image_urls": get_images_from_html(html, page_url),
    }


def normalize_url(url: str) -> str:
    """Normalize a URL by removing the scheme, port, www prefix, and trailing slashes.

    Args:
        url: The URL to normalize.

    Returns:
        Normalized URL string, e.g. ``https://www.example.com/path/`` -> ``example.com/path``.

    Raises:
        ValueError: If url is empty.
    """
    if not url:
        raise ValueError("url cannot be empty")

    logger.debug("input url: ", url)

    parts = urlsplit(url)
    logger.debug("url split into parts: %s", parts)

    sanitized = parts.hostname or ""
    sanitized += parts.path.rstrip("/")

    while sanitized.startswith("www."):
        sanitized = sanitized[4:]

    return sanitized


def get_h1_from_html(html: str) -> str:
    """Extract the text content of the first h1 element from an HTML string.

    Args:
        html: Raw HTML string to parse.

    Returns:
        Stripped text content of the first h1, or empty string if none found.

    Raises:
        ValueError: If html is empty.
    """
    if not html:
        raise ValueError("html string cannot be empty")

    soup = BeautifulSoup(html, "html.parser")
    h1 = soup.find("h1")
    return h1.get_text().strip() if h1 else ""


def get_first_paragraph_from_html(html: str) -> str:
    """Extract the text content of the first paragraph from an HTML string.

    Searches within a <main> tag if present, otherwise falls back to the
    first <p> in the document.

    Args:
        html: Raw HTML string to parse.

    Returns:
        Stripped text content of the first paragraph, or empty string if none found.

    Raises:
        ValueError: If html is empty.
    """
    if not html:
        raise ValueError("html string cannot be empty")

    soup = BeautifulSoup(html, "html.parser")
    main = soup.find("main")

    p = main.find("p") if isinstance(main, Tag) else soup.find("p")
    return p.get_text().strip() if p else ""


def get_urls_from_html(html: str, base_url: str) -> list[str]:
    """Extract and resolve all hyperlinks from an HTML string.

    Relative URLs are resolved against base_url. Absolute URLs are returned as-is.

    Args:
        html: Raw HTML string to parse.
        base_url: Base URL used to resolve relative links.

    Returns:
        List of unnormalized, resolved URL strings. Empty list if no links found.

    Raises:
        ValueError: If html or base_url is empty.
    """
    if not html or not base_url:
        raise ValueError("html string or base_url cannot be empty")

    soup = BeautifulSoup(html, "html.parser")
    links: list[str] = []

    for a in soup.find_all("a"):
        if not isinstance(a, Tag):
            continue

        link = a.get("href")
        if link is None:
            continue
        link = str(link)

        # handle common malformed url edge case
        if link.startswith("www."):
            link = "https://" + link

        # urljoin will not join absolute urls
        link = urljoin(base_url, link)
        links.append(link)

    return links


def get_images_from_html(html: str, base_url: str) -> list[str]:
    """Extract and resolve all image sources from an HTML string.

    Relative src paths are resolved against base_url. Absolute URLs are returned as-is.

    Args:
        html: Raw HTML string to parse.
        base_url: Base URL used to resolve relative image paths.

    Returns:
        List of unnormalized, resolved image URL strings. Empty list if no images found.

    Raises:
        ValueError: If html or base_url is empty.
    """
    if not html or not base_url:
        raise ValueError("html string or base_url cannot be empty")

    soup = BeautifulSoup(html, "html.parser")
    images: list[str] = []

    for img in soup.find_all("img"):
        if not isinstance(img, Tag):
            continue

        src = img.get("src")
        if src is None:
            continue
        src = str(src)

        if src.startswith("www."):
            src = "https://" + src

        src = urljoin(base_url, src)
        images.append(src)

    return images
