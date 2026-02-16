"""
Rabitabank.az partner data scraper
API: GET /castnye-klienty/partnery?search=&category=&city=0&cashback=0&sorting=all&page={N}
     with X-Requested-With: XMLHttpRequest and X-XSRF-Token header

Auth notes (Laravel):
  - Must load the partners page first to receive session cookie + XSRF-TOKEN cookie
  - XSRF-TOKEN cookie value (URL-decoded) is sent back as X-XSRF-Token request header
  - CookieJar handles the Rabitabank session cookie automatically
  - Pagination stops when response partners list is empty
"""

import csv
import http.cookiejar
import json
import time
import urllib.parse
import urllib.request
from pathlib import Path

BASE = "https://www.rabitabank.com"
PARTNERS_URL = f"{BASE}/castnye-klienty/partnery"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "rabitabank.csv"

UA = (
    "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
    "AppleWebKit/537.36 (KHTML, like Gecko) "
    "Chrome/144.0.0.0 Safari/537.36"
)

CSV_FIELDS = [
    "id",
    "title",
    "cash_back",
    "category",
    "url",
    "image_url",
    "page_scraped",
]


def make_opener() -> tuple[urllib.request.OpenerDirector, str]:
    """Open the partners page, collect session cookies, return opener + XSRF token."""
    cj = http.cookiejar.CookieJar()
    opener = urllib.request.build_opener(urllib.request.HTTPCookieProcessor(cj))
    req = urllib.request.Request(
        PARTNERS_URL,
        headers={
            "user-agent": UA,
            "accept": "text/html,application/xhtml+xml,*/*;q=0.8",
        },
    )
    opener.open(req, timeout=20).close()

    xsrf = urllib.parse.unquote(
        next(c.value for c in cj if c.name == "XSRF-TOKEN")
    )
    return opener, xsrf


def fetch_page(opener: urllib.request.OpenerDirector, xsrf: str, page: int) -> list[dict]:
    """Fetch one page from the partners API. Returns list of partner dicts (empty = done)."""
    params = urllib.parse.urlencode({
        "search": "",
        "category": "",
        "city": "0",
        "cashback": "0",
        "sorting": "all",
        "page": page,
    })
    req = urllib.request.Request(
        f"{PARTNERS_URL}?{params}",
        headers={
            "user-agent": UA,
            "accept": "application/json, text/plain, */*",
            "referer": PARTNERS_URL,
            "x-requested-with": "XMLHttpRequest",
            "x-xsrf-token": xsrf,
            "dnt": "1",
        },
    )
    with opener.open(req, timeout=20) as resp:
        data = json.loads(resp.read().decode())
    return data.get("partners", [])


def flatten_partner(p: dict, page: int) -> dict:
    image = p.get("image") or {}
    return {
        "id": p.get("id"),
        "title": (p.get("title") or "").strip(),
        "cash_back": p.get("cash_back") or "",
        "category": (p.get("category") or "").strip(),
        "url": p.get("url") or "",
        "image_url": image.get("src") or "",
        "page_scraped": page,
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Loading partners page to obtain CSRF token and session cookie...")
    opener, xsrf = make_opener()
    print("Session ready.")

    all_rows: list[dict] = []
    page = 1

    while True:
        for attempt in range(3):
            try:
                partners = fetch_page(opener, xsrf, page)
                break
            except Exception as exc:
                if attempt < 2:
                    print(f"  Page {page} error: {exc} — retrying in 3s...")
                    time.sleep(3)
                else:
                    print(f"  SKIPPING page {page}: {exc}")
                    partners = None

        if partners is None:
            break

        if not partners:
            print(f"  Page {page}: empty — done.")
            break

        for p in partners:
            all_rows.append(flatten_partner(p, page))

        print(f"  Page {page}: {len(partners)} partners (total: {len(all_rows)})")
        page += 1
        time.sleep(0.4)

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"\nDone. Saved {len(all_rows)} partners -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
