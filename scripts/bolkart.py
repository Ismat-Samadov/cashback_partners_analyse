"""
Bolkart.az partner data scraper
Fetches all partners from the public API and saves to data/bolkart.csv

API notes:
  - Pagination is 1-indexed (page=0 always returns empty data)
  - requests library is blocked by WAF; urllib is used instead
  - sort param: populyarlıq (URL-encoded: populyarl%C4%B1q)
"""

import csv
import json
import math
import time
import urllib.request
import urllib.parse
from pathlib import Path

BASE_URL = "https://bolkart.az/api/bolkart-service/public/partners"
PAGE_SIZE = 100  # max observed working size
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "bolkart.csv"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "dnt": "1",
}

CSV_FIELDS = [
    "id",
    "name_az",
    "name_en",
    "name_ru",
    "description_az",
    "description_en",
    "description_ru",
    "phone_number",
    "site_url",
    "cashback",
    "category_id",
    "category_az",
    "category_en",
    "category_ru",
    "social_medias",
    "cities_count",
    "taksits",
    "icon_url",
    "logo_url",
    "status",
    "order_number",
    "is_new",
    "at_home",
    "popularity",
    "hidden",
    "insert_date",
    "branches_count",
    "home_no",
    "whatsapp_link",
]


def _multilang(obj, field="name"):
    """Return (az, en, ru) from a multilingual field object."""
    val = (obj or {}).get(field) or {}
    return val.get("az"), val.get("en"), val.get("ru")


def flatten_partner(p: dict) -> dict:
    """Flatten a nested partner JSON object into a flat CSV row."""
    name_az, name_en, name_ru = _multilang(p, "name")
    desc_az, desc_en, desc_ru = _multilang(p, "description")

    cat = p.get("partnerCategory") or {}
    cat_id = cat.get("id")
    cat_az, cat_en, cat_ru = _multilang(cat, "name")

    socials = "; ".join(
        f"{(_multilang(s, 'name')[0] or '').strip()}:{s.get('siteUrl', '')}"
        for s in (p.get("socialMedias") or [])
        if s.get("siteUrl")
    )

    taksits = "; ".join(
        str(t.get("taksit")) for t in (p.get("taksits") or [])
    )

    icon_url = (p.get("icon") or {}).get("url", "")

    return {
        "id": p.get("id"),
        "name_az": name_az,
        "name_en": name_en,
        "name_ru": name_ru,
        "description_az": desc_az,
        "description_en": desc_en,
        "description_ru": desc_ru,
        "phone_number": p.get("phoneNumber"),
        "site_url": p.get("siteUrl"),
        "cashback": p.get("cashback"),
        "category_id": cat_id,
        "category_az": cat_az,
        "category_en": cat_en,
        "category_ru": cat_ru,
        "social_medias": socials,
        "cities_count": len(p.get("cities") or []),
        "taksits": taksits,
        "icon_url": icon_url,
        "logo_url": p.get("logoUrl"),
        "status": p.get("status"),
        "order_number": p.get("orderNumber"),
        "is_new": p.get("isNew"),
        "at_home": p.get("atHome"),
        "popularity": p.get("popularity"),
        "hidden": p.get("hidden"),
        "insert_date": p.get("insertDate"),
        "branches_count": len(p.get("branches") or []),
        "home_no": p.get("homeNo"),
        "whatsapp_link": p.get("whatsappLink"),
    }


def fetch_page(page: int, size: int = PAGE_SIZE) -> dict:
    """Fetch a single page from the partners API using urllib (requests is WAF-blocked)."""
    params = urllib.parse.urlencode({
        "page": page,
        "size": size,
        "popularity": "true",
        "sort": "populyarl\u0131q",  # ı = U+0131
    })
    url = f"{BASE_URL}?{params}"
    referer = (
        f"https://bolkart.az/az/partnyorlar"
        f"?page={page}&size={size}&popularity=true&sort=populyarl%C4%B1q"
    )
    req = urllib.request.Request(url, headers={**HEADERS, "referer": referer})
    with urllib.request.urlopen(req, timeout=20) as resp:
        return json.loads(resp.read().decode())


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    # API is 1-indexed — page=0 always returns empty data
    print("Fetching page 1 to determine total count...")
    first = fetch_page(page=1)
    total = first.get("totalElements", 0)
    total_pages = math.ceil(total / PAGE_SIZE)
    print(f"Total partners: {total} | Page size: {PAGE_SIZE} | Pages: {total_pages}")

    all_rows = []

    for p in first.get("data", []):
        all_rows.append(flatten_partner(p))
    print(f"  Page 1: {len(first.get('data', []))} partners")

    for page in range(2, total_pages + 1):
        for attempt in range(2):
            try:
                result = fetch_page(page=page)
                items = result.get("data", [])
                for p in items:
                    all_rows.append(flatten_partner(p))
                print(
                    f"  Page {page}: {len(items)} partners "
                    f"(running total: {len(all_rows)})"
                )
                time.sleep(0.4)
                break
            except Exception as exc:
                if attempt == 0:
                    print(f"  Page {page} error: {exc} — retrying after 3s...")
                    time.sleep(3)
                else:
                    print(f"  SKIPPING page {page}: {exc}")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDone. Saved {len(all_rows)} partners -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
