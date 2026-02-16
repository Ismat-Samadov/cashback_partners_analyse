"""
Birbank.az partner data scraper
Uses Next.js SSR data endpoint: /_next/data/{buildId}/az/partners.json?size={page}

API notes:
  - `size` query param = page number (1-indexed), NOT page size
  - Page size is fixed at 12; total partners ~2012 across ~168 pages
  - BuildId is extracted dynamically from the HTML to survive site rebuilds
"""

import csv
import json
import re
import time
import urllib.request
from pathlib import Path

BASE = "https://birbank.az"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "birbank.csv"

HEADERS = {
    "accept": "text/html,application/xhtml+xml,*/*;q=0.8",
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "dnt": "1",
}

CSV_FIELDS = [
    "id",
    "name",
    "slug",
    "cashback",
    "birbonus",
    "umico_bonus",
    "categories",
    "cities",
    "installments",
    "max_taksit_month",
    "payment_methods",
    "is_bnpl",
    "has_barcode",
    "phone",
    "website",
    "instagram",
    "facebook",
    "voen",
    "image_url",
    "order",
    "created_at",
    "updated_at",
    "published_at",
]


def fetch(url: str, extra_headers: dict | None = None) -> bytes:
    headers = {**HEADERS, **(extra_headers or {})}
    req = urllib.request.Request(url, headers=headers)
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read()


def get_build_id() -> str:
    html = fetch(f"{BASE}/partners").decode("utf-8", errors="replace")
    m = re.search(r'"buildId"\s*:\s*"([^"]+)"', html)
    if not m:
        raise ValueError("buildId not found — site structure may have changed")
    return m.group(1)


def fetch_page(build_id: str, page: int) -> dict:
    url = f"{BASE}/_next/data/{build_id}/az/partners.json?size={page}"
    raw = fetch(
        url,
        extra_headers={
            "accept": "*/*",
            "referer": f"{BASE}/az/partners",
            "x-nextjs-data": "1",
        },
    )
    return json.loads(raw.decode())


def _join_strapi_list(obj: dict | list | None, key: str) -> str:
    """Extract a semicolon-joined list from a Strapi {data:[{attributes:{key:...}}]} structure."""
    if not obj:
        return ""
    data = obj.get("data", []) if isinstance(obj, dict) else obj
    if not isinstance(data, list):
        return ""
    parts = []
    for item in data:
        if isinstance(item, dict):
            attrs = item.get("attributes", item)
            val = attrs.get(key)
            if val:
                parts.append(str(val).strip())
    return "; ".join(parts)


def flatten_partner(raw: dict) -> dict:
    pid = raw.get("id")
    a = raw.get("attributes", {})

    image_url = ""
    img = a.get("image") or {}
    img_data = img.get("data") or {}
    if isinstance(img_data, dict):
        image_url = (img_data.get("attributes") or {}).get("url", "")

    categories = _join_strapi_list(a.get("categories"), "categoryName")
    cities = _join_strapi_list(a.get("cities"), "name")
    installments = _join_strapi_list(a.get("installments"), "duration")
    payment_methods = _join_strapi_list(a.get("paymentMethod"), "name")

    return {
        "id": pid,
        "name": (a.get("name") or "").strip(),
        "slug": a.get("slug") or "",
        "cashback": a.get("cashback") or "",
        "birbonus": a.get("birbonus") or "",
        "umico_bonus": a.get("umicoBonus") or "",
        "categories": categories,
        "cities": cities,
        "installments": installments,
        "max_taksit_month": a.get("maxTaksitMonth") or "",
        "payment_methods": payment_methods,
        "is_bnpl": a.get("isBNPL") or "",
        "has_barcode": a.get("hasBarcode") or "",
        "phone": a.get("phone") or "",
        "website": a.get("website") or "",
        "instagram": a.get("instagram") or "",
        "facebook": a.get("facebook") or "",
        "voen": a.get("voen") or "",
        "image_url": image_url,
        "order": a.get("order") or "",
        "created_at": a.get("createdAt") or "",
        "updated_at": a.get("updatedAt") or "",
        "published_at": a.get("publishedAt") or "",
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Fetching buildId from /partners HTML...")
    build_id = get_build_id()
    print(f"BuildId: {build_id}")

    print("Fetching page 1 to determine total pages...")
    first = fetch_page(build_id, page=1)
    pagination = first["pageProps"]["initialState"]["partners"]["pagination"]
    total = pagination["total"]
    page_count = pagination["pageCount"]
    print(f"Total partners: {total} | Pages: {page_count}")

    all_rows: list[dict] = []

    for raw in first["pageProps"]["initialState"]["partners"]["partnersData"]:
        all_rows.append(flatten_partner(raw))
    print(f"  Page 1: {len(first['pageProps']['initialState']['partners']['partnersData'])} partners")

    for page in range(2, page_count + 1):
        for attempt in range(2):
            try:
                result = fetch_page(build_id, page=page)
                items = result["pageProps"]["initialState"]["partners"]["partnersData"]
                for raw in items:
                    all_rows.append(flatten_partner(raw))
                print(f"  Page {page}/{page_count}: {len(items)} partners (total: {len(all_rows)})")
                time.sleep(0.3)
                break
            except Exception as exc:
                if attempt == 0:
                    print(f"  Page {page} error: {exc} — retrying in 3s...")
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
