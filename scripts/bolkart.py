"""
Bolkart.az partner data scraper
Fetches all partners from the public API and saves to data/bolkart.csv
"""

import csv
import math
import time
from pathlib import Path

import requests

BASE_URL = "https://bolkart.az/api/bolkart-service/public/partners"
PAGE_SIZE = 50
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "bolkart.csv"

HEADERS = {
    "accept": "application/json, text/plain, */*",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "dnt": "1",
    "sec-fetch-mode": "cors",
    "sec-fetch-site": "same-origin",
    "sec-fetch-dest": "empty",
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
    """Extract az/en/ru values from a multilingual field object."""
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


def fetch_page(session: requests.Session, page: int, size: int = PAGE_SIZE) -> dict:
    """Fetch a single page from the partners API."""
    params = {
        "page": page,
        "size": size,
        "popularity": "true",
        "sort": "populyarl\u0131q",  # populyarlıq
    }
    referer = (
        f"https://bolkart.az/az/partnyorlar"
        f"?page={page}&size={size}&popularity=true&sort=populyarl%C4%B1q"
    )
    headers = {**HEADERS, "referer": referer}
    resp = session.get(BASE_URL, params=params, headers=headers, timeout=20)
    resp.raise_for_status()
    return resp.json()


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    session = requests.Session()

    print("Fetching page 0 to determine total count...")
    first = fetch_page(session, page=0)
    total = first.get("totalElements", 0)
    total_pages = math.ceil(total / PAGE_SIZE)
    print(f"Total partners: {total} | Page size: {PAGE_SIZE} | Pages: {total_pages}")

    all_rows = []

    # Process page 0
    for p in first.get("data", []):
        all_rows.append(flatten_partner(p))
    print(f"  Page 0: {len(first.get('data', []))} partners")

    # Fetch remaining pages
    for page in range(1, total_pages):
        try:
            result = fetch_page(session, page=page)
            items = result.get("data", [])
            for p in items:
                all_rows.append(flatten_partner(p))
            print(f"  Page {page}: {len(items)} partners (running total: {len(all_rows)})")
            time.sleep(0.4)
        except requests.RequestException as exc:
            print(f"  ERROR on page {page}: {exc} — retrying after 3s...")
            time.sleep(3)
            try:
                result = fetch_page(session, page=page)
                items = result.get("data", [])
                for p in items:
                    all_rows.append(flatten_partner(p))
                print(f"  Page {page} (retry): {len(items)} partners")
            except Exception as exc2:
                print(f"  SKIPPING page {page} after retry: {exc2}")

    # Write CSV
    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDone. Saved {len(all_rows)} partners -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
