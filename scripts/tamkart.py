"""
Tamkart.az partner data scraper
All partner data is embedded as a static JS array in the Next.js bundle
(no pagination API — "Daha çox" button is purely client-side slice of the array).

Strategy:
  1. Fetch /partners HTML → extract buildId
  2. Fetch build manifest → locate the chunk containing module 5243 (partner list)
  3. Extract the JS array with bracket matching
  4. Parse JS object-literal notation via Node.js (keys are unquoted → invalid JSON)
  5. Write data/tamkart.csv
"""

import csv
import json
import re
import subprocess
import sys
import tempfile
import urllib.request
from pathlib import Path

BASE = "https://tamkart.az"
OUTPUT_PATH = Path(__file__).parent.parent / "data" / "tamkart.csv"

HEADERS = {
    "user-agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/144.0.0.0 Safari/537.36"
    ),
    "accept": "text/html,application/xhtml+xml,*/*;q=0.8",
}

CSV_FIELDS = [
    "id",
    "name",
    "city",
    "category",
    "cashback",
    "taksits",
    "taksit_condition",
    "address",
    "map_lat",
    "map_lng",
    "parent_id",
]


def fetch(url: str, accept: str = "text/html") -> str:
    req = urllib.request.Request(
        url, headers={**HEADERS, "accept": accept, "referer": BASE + "/partners"}
    )
    with urllib.request.urlopen(req, timeout=20) as resp:
        return resp.read().decode("utf-8", errors="replace")


def get_build_id(html: str) -> str:
    m = re.search(r'"buildId"\s*:\s*"([^"]+)"', html)
    if not m:
        raise ValueError("buildId not found in HTML")
    return m.group(1)


def get_chunk_urls(build_id: str) -> list[str]:
    """Fetch build manifest and return all static chunk URLs."""
    manifest_url = f"{BASE}/_next/static/{build_id}/_buildManifest.js"
    content = fetch(manifest_url, accept="*/*")
    return re.findall(r'static/chunks/[^"\']+\.js', content)


def find_partner_chunk(chunk_urls: list[str]) -> str | None:
    """Return the chunk JS text that contains module 5243 (partner list)."""
    for path in chunk_urls:
        url = f"{BASE}/_next/{path}"
        try:
            js = fetch(url, accept="*/*")
            if "5243" in js and "let s=[" in js:
                print(f"  Partner data chunk: {path}")
                return js
        except Exception:
            continue
    return None


def extract_js_array(js: str) -> str:
    """Extract the full JS array assigned to `let s=[...]` using bracket matching."""
    start = js.find("let s=[") + len("let s=")
    if start < len("let s="):
        raise ValueError("Could not find 'let s=[' in JS")
    depth = 0
    in_str = False
    escape = False
    str_char = None
    end = start
    for i, ch in enumerate(js[start:], start):
        if escape:
            escape = False
            continue
        if ch == "\\":
            escape = True
            continue
        if in_str:
            if ch == str_char:
                in_str = False
            continue
        if ch in ('"', "'", "`"):
            in_str = True
            str_char = ch
            continue
        if ch == "[":
            depth += 1
        elif ch == "]":
            depth -= 1
            if depth == 0:
                end = i + 1
                break
    return js[start:end]


def parse_js_array(arr_str: str) -> list[dict]:
    """Use Node.js to evaluate the JS object-literal array (unquoted keys → not JSON)."""
    js_code = f"process.stdout.write(JSON.stringify({arr_str}));"
    with tempfile.NamedTemporaryFile(
        mode="w", suffix=".js", delete=False, encoding="utf-8"
    ) as tmp:
        tmp.write(js_code)
        tmp_path = tmp.name
    result = subprocess.run(
        ["node", tmp_path], capture_output=True, text=True, timeout=30
    )
    if result.returncode != 0:
        raise RuntimeError(f"Node.js error: {result.stderr[:500]}")
    return json.loads(result.stdout)


def parse_coords(map_str: str) -> tuple[str, str]:
    """Split 'lat, lng' map string into separate lat/lng strings."""
    if not map_str:
        return "", ""
    parts = map_str.strip().split(",")
    lat = parts[0].strip() if parts else ""
    lng = parts[1].strip() if len(parts) > 1 else ""
    return lat, lng


def flatten_partner(p: dict) -> dict:
    lat, lng = parse_coords(p.get("map", ""))
    return {
        "id": p.get("id"),
        "name": (p.get("name") or "").strip(),
        "city": (p.get("city") or "").strip(),
        "category": (p.get("category") or "").strip(),
        "cashback": p.get("cashback") or "",
        "taksits": p.get("taksits") or "",
        "taksit_condition": p.get("taksit_condition") or "",
        "address": (p.get("address") or "").strip(),
        "map_lat": lat,
        "map_lng": lng,
        "parent_id": p.get("parent", ""),
    }


def main():
    OUTPUT_PATH.parent.mkdir(parents=True, exist_ok=True)

    print("Fetching /partners page...")
    html = fetch(f"{BASE}/partners")
    build_id = get_build_id(html)
    print(f"Build ID: {build_id}")

    print("Fetching build manifest...")
    chunk_urls = get_chunk_urls(build_id)
    print(f"Found {len(chunk_urls)} chunk(s)")

    print("Locating partner data chunk (module 5243)...")
    js = find_partner_chunk(chunk_urls)
    if not js:
        sys.exit("ERROR: Partner data chunk not found — the site may have been rebuilt.")

    print("Extracting JS array...")
    arr_str = extract_js_array(js)
    print(f"Array size: {len(arr_str):,} chars")

    print("Parsing via Node.js...")
    partners = parse_js_array(arr_str)
    print(f"Parsed {len(partners)} partners")

    rows = [flatten_partner(p) for p in partners]

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(rows)

    print(f"\nDone. Saved {len(rows)} partners -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
