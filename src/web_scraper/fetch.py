import requests


def get_html(url: str):
    r = requests.get(url, headers={"User-Agent": "BootCrawler/1.0"}, timeout=10)
    r.raise_for_status()

    if "text/html" not in r.headers.get("content-type", ""):
        raise ValueError(
            f"expected text/html, got {r.headers.get('content-type')} for url: {r.url}"
        )

    return r.text
