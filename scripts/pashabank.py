"""
PASHA Bank Miles & Smiles partner scraper
URL: https://miles.pashabank.az/az/partners

Page structure notes:
  - Drupal-based site, server-side rendered HTML
  - All 80 partners are embedded in a single page (no API, no pagination)
  - Category ID → name mapping extracted from filter links (data-category attribute)
  - Each partner block: <div class="partner-block" data-product-category="{id}">
  - Reward info in <p class="description"> as:
      "1 AZN məbləğinə əlavə [condition?]N Mil hesablanır"
  - Partner name is in &amp;-encoded HTML entity form (decoded by html.unescape)
  - Image URLs are relative, converted to absolute
"""

import csv
import html
import re
import urllib.request
from pathlib import Path

BASE = "https://miles.pashabank.az"
URL = f"{BASE}/az/partners"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "pashabank.csv"

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "accept-language": "en-GB,en-US;q=0.9,az;q=0.8",
}

CSV_FIELDS = [
    "name",
    "category",
    "category_id",
    "miles_per_azn",
    "condition",
    "image_url",
]


def fetch_html() -> str:
    req = urllib.request.Request(URL, headers=HEADERS)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def build_category_map(page_html: str) -> dict[str, str]:
    """Extract category id → name from the filter link elements."""
    cats = re.findall(r'data-category="(\d+)"[^>]*>([^<]+)<', page_html)
    return {cid: name.strip() for cid, name in cats if cid != "0"}


def strip_tags(raw: str) -> str:
    """Remove HTML tags and collapse whitespace."""
    return re.sub(r"\s+", " ", re.sub(r"<[^>]+>", " ", raw)).strip()


def extract_miles(desc_text: str) -> str:
    """Extract the miles-per-AZN number from the description plain text."""
    m = re.search(r"([\d.]+)\s*Mil\s*hesablanır", desc_text)
    return m.group(1) if m else ""


def extract_condition(desc_html: str) -> str:
    """
    Extract the optional condition note (text between 'əlavə' and the miles number).
    The tooltip span wraps the condition text inside the description paragraph.
    """
    # Remove the standard wrapping phrase and the miles conclusion
    text = strip_tags(desc_html)
    text = re.sub(r"1 AZN məbləğinə əlavə\s*", "", text)
    text = re.sub(r"[\d.]+\s*Mil hesablanır", "", text).strip()
    return text


def parse_partners(page_html: str, cat_map: dict[str, str]) -> list[dict]:
    """Split on partner-block divs and parse each one."""
    blocks = re.split(r"(?=<div class=\"partner-block\")", page_html)
    rows = []
    for block in blocks[1:]:
        cat_id_m = re.search(r'data-product-category="(\d+)"', block)
        img_m = re.search(r'data-src="([^"]+)"', block)
        name_m = re.search(r'class="partner__name">(.*?)</h2>', block, re.DOTALL)
        ptype_m = re.search(r'class="partners__type">(.*?)</p>', block, re.DOTALL)
        desc_m = re.search(r'class="description">(.*?)</p>', block, re.DOTALL)

        cat_id = cat_id_m.group(1) if cat_id_m else ""
        desc_html_raw = desc_m.group(1) if desc_m else ""
        desc_text = strip_tags(desc_html_raw)

        # Partner name (HTML-entity decode)
        name_raw = strip_tags(name_m.group(1)) if name_m else ""
        name = html.unescape(name_raw)

        # Category name: from inline <p> first, then from the filter map
        cat_name = strip_tags(ptype_m.group(1)) if ptype_m else cat_map.get(cat_id, "")

        # Image URL (relative → absolute)
        img_src = img_m.group(1) if img_m else ""
        if img_src and not img_src.startswith("http"):
            img_src = BASE + img_src

        rows.append({
            "name": name,
            "category": cat_name,
            "category_id": cat_id,
            "miles_per_azn": extract_miles(desc_text),
            "condition": extract_condition(desc_html_raw),
            "image_url": img_src,
        })
    return rows


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print(f"Fetching {URL} ...")
    page_html = fetch_html()

    cat_map = build_category_map(page_html)
    print(f"Categories found: {len(cat_map)}")

    rows = parse_partners(page_html, cat_map)
    print(f"Partners parsed: {len(rows)}")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Saved {len(rows)} partners -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
