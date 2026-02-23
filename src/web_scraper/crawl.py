import logging
from urllib.parse import urlsplit

from bs4 import BeautifulSoup, Tag

logger = logging.getLogger(__name__)


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
