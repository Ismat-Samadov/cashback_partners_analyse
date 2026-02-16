"""
Xalqbank.az XalqKart Cashback partner scraper
API: GET /api/az/ferdi/kartlar/xalqkart-cashback/terefdaslar?include=menu

API notes:
  - Single request returns all partners (no pagination)
  - Response: data.blocks[type="card-partners"].blocks = list of partner objects
  - Each partner has: id, title, image, percent, body (HTML), category, region
  - body HTML contains address and contact info (phone, website, social links)
  - Session cookie (xalqbank) is set on first page load — included automatically by CookieJar
"""

import csv
import http.cookiejar
import json
import re
import urllib.request
from pathlib import Path

BASE = "https://www.xalqbank.az"
API_URL = f"{BASE}/api/az/ferdi/kartlar/xalqkart-cashback/terefdaslar?include=menu"
PAGE_URL = f"{BASE}/az/ferdi/kartlar/xalqkart-cashback/terefdaslar"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "xalqbank.csv"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/144.0.0.0 Safari/537.36"
)

CSV_FIELDS = [
    "id",
    "title",
    "cashback_percent",
    "category",
    "category_id",
    "region",
    "region_id",
    "address",
    "phone",
    "website",
    "image_url",
    "body_html",
]


def make_opener() -> urllib.request.OpenerDirector:
    """Load the partner page to obtain the session cookie, return configured opener."""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    opener.open(
        urllib.request.Request(
            PAGE_URL,
            headers={"user-agent": UA, "accept": "text/html,*/*;q=0.8"},
        ),
        timeout=20,
    ).close()
    return opener


def fetch_partners(opener: urllib.request.OpenerDirector) -> list[dict]:
    """Call the API and return the raw partner list."""
    req = urllib.request.Request(
        API_URL,
        headers={
            "user-agent": UA,
            "accept": "application/json, text/plain, */*",
            "referer": PAGE_URL,
            "x-requested-with": "XMLHttpRequest",
            "cache-control": "no-cache",
            "pragma": "no-cache",
            "dnt": "1",
        },
    )
    with opener.open(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())

    # Navigate: data.data.blocks[type="card-partners"].blocks
    for block in data["data"]["blocks"]:
        if block.get("type") == "card-partners":
            return block.get("blocks", [])
    return []


def strip_tags(html: str) -> str:
    """Remove HTML tags, collapse whitespace."""
    text = re.sub(r"<[^>]+>", " ", html or "")
    return re.sub(r"\s+", " ", text).strip()


def extract_body_fields(body_html: str) -> tuple[str, str, str]:
    """
    Parse the body HTML field to extract address, phone, and website.
    Typical body: <p>Address...</p><p>Tel: +994...</p><p><a href="...">...</a></p>
    """
    body_html = body_html or ""

    # Phone numbers
    phones = re.findall(r"(?:Tel[:\s]*)?(\+?994[\d\s\-\(\)]{7,}|\(?0\d{2}\)?[\s\-]?\d{3}[\s\-]?\d{2}[\s\-]?\d{2})", body_html)
    phone = "; ".join(p.strip() for p in phones[:3]) if phones else ""

    # URLs from anchor tags
    links = re.findall(r'href=["\']([^"\']+)["\']', body_html)
    websites = [l for l in links if l.startswith("http") and "xalqbank" not in l and "instagram" not in l.lower() and "facebook" not in l.lower()]
    social = [l for l in links if "instagram" in l.lower() or "facebook" in l.lower()]
    website = websites[0] if websites else (social[0] if social else "")

    # Address: first <p> paragraph text that isn't a phone or link
    paragraphs = re.findall(r"<p>(.*?)</p>", body_html, re.DOTALL)
    address = ""
    for p in paragraphs:
        text = strip_tags(p).strip()
        if text and "Tel" not in text and not text.startswith("+") and "href" not in p:
            address = text
            break

    return address, phone, website


def flatten_partner(p: dict) -> dict:
    cat = p.get("category") or {}
    region = p.get("region") or {}
    image = p.get("image") or {}
    body_html = p.get("body") or ""

    address, phone, website = extract_body_fields(body_html)

    return {
        "id": p.get("id"),
        "title": (p.get("title") or "").strip(),
        "cashback_percent": p.get("percent") or "",
        "category": (cat.get("title") or "").strip(),
        "category_id": cat.get("id") or "",
        "region": (region.get("title") or "").strip(),
        "region_id": region.get("id") or "",
        "address": address,
        "phone": phone,
        "website": website,
        "image_url": image.get("src") or "",
        "body_html": re.sub(r"\s+", " ", body_html).strip(),
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Loading partner page to obtain session cookie...")
    opener = make_opener()

    print("Fetching partner data from API...")
    raw_partners = fetch_partners(opener)
    print(f"Received {len(raw_partners)} partners")

    rows = [flatten_partner(p) for p in raw_partners]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Saved {len(rows)} partners -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
