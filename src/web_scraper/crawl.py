from urllib.parse import urlsplit
import logging

logger = logging.getLogger(__name__)


def normalize_url(url: str) -> str:
    if not url:
        raise ValueError("url cannot be empty")

    logger.debug("input url: ", url)

    parts = urlsplit(url)
    logger.debug("url split into parts: %s", parts)

    sanitized = parts.hostname or ""
    sanitized += parts.path.rstrip("/")
    sanitized = sanitized.lstrip("www.")

    return sanitized
