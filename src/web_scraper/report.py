import csv
from .html_parse import PageData
from pathlib import Path

DEFAULT_OUT = "./out/"


def write_csv_report(pages: dict[str, PageData], filename: str = "report.csv"):
    filepath = Path(DEFAULT_OUT, filename)
    filepath.parent.mkdir(parents=True, exist_ok=True)

    with open(filepath, "w", newline="", encoding="utf-8-sig") as csvfile:
        fieldnames = [
            "page_url",
            "h1",
            "first_paragraph",
            "outgoing_link_urls",
            "image_urls",
        ]
        writer = csv.DictWriter(csvfile, fieldnames)

        writer.writeheader()
        for url, page in pages.items():
            writer.writerow(
                {
                    "page_url": url,
                    "h1": page["h1"],
                    "first_paragraph": page["first_paragraph"],
                    "outgoing_link_urls": ";".join(page["outgoing_links"]),
                    "image_urls": ";".join(page["image_urls"]),
                }
            )
