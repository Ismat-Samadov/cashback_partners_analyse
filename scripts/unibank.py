"""
Unibank.az U-Card partner data scraper
URL: https://unibank.az/cards/ucardpartners?page={N}

Page structure notes:
  - Server-side rendered HTML, no JSON API
  - Each partner appears TWICE per page (hidden--mobile = desktop, hidden--desc = mobile)
  - Only 'hidden--mobile' blocks are parsed to avoid duplicates
  - Pagination stops when the first-partner ID has already been seen (page repeats at the end)
  - 3 real pages (88 + 96 + 78 = 262 partners)

Fields extracted per partner:
  data-partner   → partner ID
  data-cat       → category ID
  data-percent   → cashback percentage (often empty)
  feature__value → partner name
  feature__desc  → category name
  feature__img   → logo image src
  anchor href    → detail page URL
  month{N} divs  → available taksit months (comma-joined)
"""

import csv
import re
import time
import urllib.request
from pathlib import Path

BASE = "https://unibank.az"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "unibank.csv"

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "accept-language": "en-GB,en-US;q=0.9,en;q=0.8",
}

CSV_FIELDS = [
    "id",
    "name",
    "category",
    "category_id",
    "cashback_percent",
    "taksit_months",
    "detail_url",
    "image_url",
]

# Split marker: only parse desktop variant to avoid duplicates
BLOCK_MARKER = 'feature feature--alb feature--cashbackpartners hidden--mobile'


def fetch_html(page: int) -> str:
    url = f"{BASE}/cards/ucardpartners?page={page}"
    req = urllib.request.Request(url, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def parse_page(html: str) -> list[dict]:
    """Extract all desktop partner blocks from a page's HTML."""
    blocks = re.split(rf"(?=<div class=\"{re.escape(BLOCK_MARKER)}\")", html)
    rows = []
    for block in blocks[1:]:
        row = parse_block(block)
        if row:
            rows.append(row)
    return rows


def _text(pattern: str, html: str, group: int = 1, default: str = "") -> str:
    m = re.search(pattern, html, re.DOTALL)
    return m.group(group).strip() if m else default


def parse_block(block: str) -> dict | None:
    pid = _text(r'data-partner="(\d+)"', block)
    if not pid:
        return None

    name = _text(r'feature__value--partners">\s*([^\s<][^<]*?)\s*</div>', block)
    category = _text(r'feature__desc--partners1">\s*([^\s<][^<]*?)\s*</div>', block)
    category_id = _text(r'data-cat="([^"]*)"', block)
    cashback = _text(r'data-percent="([^"]*)"', block)

    # Logo image URL (relative → absolute)
    img_src = _text(r'feature__img[^>]+src="([^"]+)"', block)
    if img_src and not img_src.startswith("http"):
        img_src = BASE + img_src

    # Detail page URL
    detail_url = _text(r'href="(/[^"]*partner/\d+[^"]*)"', block)
    if detail_url and not detail_url.startswith("http"):
        detail_url = BASE + detail_url

    # Taksit months available (e.g. "3, 6, 12")
    months = re.findall(r'<div class="month(\d+) feature--taksit-item', block)
    taksit_months = ", ".join(sorted(set(months), key=int)) if months else ""

    return {
        "id": pid,
        "name": name,
        "category": category,
        "category_id": category_id,
        "cashback_percent": cashback,
        "taksit_months": taksit_months,
        "detail_url": detail_url,
        "image_url": img_src,
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    all_rows: list[dict] = []
    seen_first_id: str | None = None
    page = 1

    while True:
        html = fetch_html(page)
        rows = parse_page(html)

        if not rows:
            print(f"  Page {page}: no partners found — stopping.")
            break

        first_id = rows[0]["id"]
        if seen_first_id is not None and first_id == seen_first_id:
            print(f"  Page {page}: duplicate of previous page — stopping.")
            break

        # Track first ID of first page to detect cycles
        if page == 1:
            seen_first_id = first_id

        # Check for repeated content vs last page's first ID
        if len(all_rows) > 0 and first_id == all_rows[-len(rows)]["id"] if len(all_rows) >= len(rows) else False:
            print(f"  Page {page}: duplicate content — stopping.")
            break

        all_rows.extend(rows)
        print(f"  Page {page}: {len(rows)} partners (total: {len(all_rows)})")
        page += 1
        time.sleep(0.4)

    # Deduplicate by partner ID (keep first occurrence)
    seen_ids: set[str] = set()
    unique_rows = []
    for r in all_rows:
        if r["id"] not in seen_ids:
            seen_ids.add(r["id"])
            unique_rows.append(r)

    if len(unique_rows) < len(all_rows):
        print(f"Deduplication: {len(all_rows)} → {len(unique_rows)} rows")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(unique_rows)

    print(f"\nDone. Saved {len(unique_rows)} partners -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
