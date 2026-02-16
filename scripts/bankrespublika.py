"""
Bank Respublika partner scraper
URL: https://www.bankrespublika.az/az/pages/partnyorlar

Page structure notes:
  - jQuery/Bootstrap site, server-side rendered HTML
  - All 416 partner branches are embedded in a single unclosed <table class="contentTable">
  - No pagination, no AJAX, no API — one request fetches all data
  - Table has no <thead>, each <tr> has 3 <td> cells:
      col 0: partner/merchant name
      col 1: address
      col 2: city
  - HTML entities (&ccedil;, &nbsp; etc.) decoded via html.unescape()
  - 416 rows represent individual branch locations (not unique companies)
"""

import csv
import html
import re
import urllib.request
from pathlib import Path

BASE = "https://www.bankrespublika.az"
URL = f"{BASE}/az/pages/partnyorlar"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "bankrespublika.csv"

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "accept-language": "az-AZ,az;q=0.9,en;q=0.8",
}

CSV_FIELDS = ["name", "address", "city"]


def fetch_html() -> str:
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def strip_tags(raw: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)).strip()


def parse_partners(page_html: str) -> list[dict]:
    """
    Extract all rows from the contentTable.

    The table tag is unclosed in the HTML (malformed), so we locate it by
    searching for the opening tag and read all <tr>…</tr> blocks from that
    position onward.
    """
    table_start = page_html.find('<table class="contentTable"')
    if table_start == -1:
        raise ValueError("contentTable not found in page HTML")

    table_region = page_html[table_start:]
    rows = []

    for tr in re.findall(r"<tr>(.*?)</tr>", table_region, re.DOTALL):
        tds = re.findall(r"<td[^>]*>(.*?)</td>", tr, re.DOTALL)
        if len(tds) < 3:
            continue

        name = html.unescape(strip_tags(tds[0])).replace("\xa0", " ").strip()
        address = html.unescape(strip_tags(tds[1])).replace("\xa0", " ").strip()
        city = html.unescape(strip_tags(tds[2])).replace("\xa0", " ").strip()

        if not name:
            continue

        rows.append({"name": name, "address": address, "city": city})

    return rows


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {URL} ...")
    page_html = fetch_html()
    print(f"Page size: {len(page_html):,} bytes")

    rows = parse_partners(page_html)
    print(f"Partner branches parsed: {len(rows)}")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Saved {len(rows)} rows -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
