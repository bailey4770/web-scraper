from urllib.parse import urlsplit
import logging

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
    sanitized = sanitized.lstrip("www.")

    return sanitized
