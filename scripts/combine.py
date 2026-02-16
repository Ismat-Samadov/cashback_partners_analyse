"""
Combine all bank partner CSVs into a single data/data.csv.

Unified schema
--------------
source          : bank identifier (bolkart, tamkart, birbank, rabitabank,
                  unibank, xalqbank, pashabank, bankrespublika)
id              : original partner ID (empty if source has none)
name            : partner / merchant name
category        : category name (Azerbaijani where available)
cashback        : numeric reward value (cashback % or miles per AZN)
reward_type     : cashback | miles | taksit_only | unknown
taksit_months   : installment month options (comma-separated integers)
city            : city / region
address         : physical address
phone           : phone number(s)
website         : partner website URL
image_url       : logo / image URL
"""

import csv
import re
from pathlib import Path

DATA_DIR = Path(__file__).parent.parent / "data"
OUTPUT_PATH = DATA_DIR / "data.csv"

CSV_FIELDS = [
    "source",
    "id",
    "name",
    "category",
    "cashback",
    "reward_type",
    "taksit_months",
    "city",
    "address",
    "phone",
    "website",
    "image_url",
]


# ---------------------------------------------------------------------------
# Helpers
# ---------------------------------------------------------------------------

def _clean(v) -> str:
    return str(v or "").strip()


def _cashback_num(raw: str) -> str:
    """Normalise cashback to a plain number string (strip %, handle empty)."""
    raw = _clean(raw)
    raw = raw.replace("%", "").strip()
    try:
        return str(float(raw)) if raw else ""
    except ValueError:
        return raw


def _reward_type(cashback: str, taksit: str, source: str) -> str:
    if source == "pashabank":
        return "miles"
    cb = cashback.strip()
    try:
        if cb and float(cb) > 0:
            return "cashback"
    except ValueError:
        if cb:
            return "cashback"
    if taksit.strip():
        return "taksit_only"
    return "unknown"


# ---------------------------------------------------------------------------
# Per-source transformers
# ---------------------------------------------------------------------------

def load_bolkart() -> list[dict]:
    rows = []
    with open(DATA_DIR / "bolkart.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cb = _cashback_num(r["cashback"])
            taksit = _clean(r["taksits"])
            rows.append({
                "source": "bolkart",
                "id": _clean(r["id"]),
                "name": _clean(r["name_az"]),
                "category": _clean(r["category_az"]),
                "cashback": cb,
                "reward_type": _reward_type(cb, taksit, "bolkart"),
                "taksit_months": taksit,
                "city": "",
                "address": "",
                "phone": _clean(r["phone_number"]),
                "website": _clean(r["site_url"]),
                "image_url": _clean(r["logo_url"]) or _clean(r["icon_url"]),
            })
    return rows


def load_tamkart() -> list[dict]:
    rows = []
    with open(DATA_DIR / "tamkart.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cb = _cashback_num(r["cashback"])
            taksit = _clean(r["taksits"])
            rows.append({
                "source": "tamkart",
                "id": _clean(r["id"]),
                "name": _clean(r["name"]),
                "category": _clean(r["category"]),
                "cashback": cb,
                "reward_type": _reward_type(cb, taksit, "tamkart"),
                "taksit_months": taksit,
                "city": _clean(r["city"]),
                "address": _clean(r["address"]),
                "phone": "",
                "website": "",
                "image_url": "",
            })
    return rows


def load_birbank() -> list[dict]:
    rows = []
    with open(DATA_DIR / "birbank.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cb = _cashback_num(r["cashback"])
            taksit = _clean(r["installments"])
            rows.append({
                "source": "birbank",
                "id": _clean(r["id"]),
                "name": _clean(r["name"]),
                "category": _clean(r["categories"]),
                "cashback": cb,
                "reward_type": _reward_type(cb, taksit, "birbank"),
                "taksit_months": taksit,
                "city": _clean(r["cities"]),
                "address": "",
                "phone": _clean(r["phone"]),
                "website": _clean(r["website"]),
                "image_url": _clean(r["image_url"]),
            })
    return rows


def load_rabitabank() -> list[dict]:
    rows = []
    with open(DATA_DIR / "rabitabank.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cb = _cashback_num(r["cash_back"])
            rows.append({
                "source": "rabitabank",
                "id": _clean(r["id"]),
                "name": _clean(r["title"]),
                "category": _clean(r["category"]),
                "cashback": cb,
                "reward_type": _reward_type(cb, "", "rabitabank"),
                "taksit_months": "",
                "city": "",
                "address": "",
                "phone": "",
                "website": _clean(r["url"]),
                "image_url": _clean(r["image_url"]),
            })
    return rows


def load_unibank() -> list[dict]:
    rows = []
    with open(DATA_DIR / "unibank.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cb = _cashback_num(r["cashback_percent"])
            taksit = _clean(r["taksit_months"])
            rows.append({
                "source": "unibank",
                "id": _clean(r["id"]),
                "name": _clean(r["name"]),
                "category": _clean(r["category"]),
                "cashback": cb,
                "reward_type": _reward_type(cb, taksit, "unibank"),
                "taksit_months": taksit,
                "city": "",
                "address": "",
                "phone": "",
                "website": _clean(r["detail_url"]),
                "image_url": _clean(r["image_url"]),
            })
    return rows


def load_xalqbank() -> list[dict]:
    rows = []
    with open(DATA_DIR / "xalqbank.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cb = _cashback_num(r["cashback_percent"])
            rows.append({
                "source": "xalqbank",
                "id": _clean(r["id"]),
                "name": _clean(r["title"]),
                "category": _clean(r["category"]),
                "cashback": cb,
                "reward_type": _reward_type(cb, "", "xalqbank"),
                "taksit_months": "",
                "city": _clean(r["region"]),
                "address": _clean(r["address"]),
                "phone": _clean(r["phone"]),
                "website": _clean(r["website"]),
                "image_url": _clean(r["image_url"]),
            })
    return rows


def load_pashabank() -> list[dict]:
    rows = []
    with open(DATA_DIR / "pashabank.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            cb = _cashback_num(r["miles_per_azn"])
            rows.append({
                "source": "pashabank",
                "id": "",
                "name": _clean(r["name"]),
                "category": _clean(r["category"]),
                "cashback": cb,          # miles per AZN
                "reward_type": "miles",
                "taksit_months": "",
                "city": "",
                "address": _clean(r["condition"]),
                "phone": "",
                "website": "",
                "image_url": _clean(r["image_url"]),
            })
    return rows


def load_bankrespublika() -> list[dict]:
    rows = []
    with open(DATA_DIR / "bankrespublika.csv", newline="", encoding="utf-8") as f:
        for r in csv.DictReader(f):
            rows.append({
                "source": "bankrespublika",
                "id": "",
                "name": _clean(r["name"]),
                "category": "",
                "cashback": "",
                "reward_type": "unknown",
                "taksit_months": "",
                "city": _clean(r["city"]),
                "address": _clean(r["address"]),
                "phone": "",
                "website": "",
                "image_url": "",
            })
    return rows


# ---------------------------------------------------------------------------
# Main
# ---------------------------------------------------------------------------

LOADERS = [
    load_bolkart,
    load_tamkart,
    load_birbank,
    load_rabitabank,
    load_unibank,
    load_xalqbank,
    load_pashabank,
    load_bankrespublika,
]


def main():
    all_rows: list[dict] = []
    for loader in LOADERS:
        rows = loader()
        source = rows[0]["source"] if rows else "?"
        print(f"  {source:20s}: {len(rows):>5} rows")
        all_rows.extend(rows)

    print(f"\nTotal rows: {len(all_rows)}")

    with open(OUTPUT_PATH, "w", newline="", encoding="utf-8") as f:
        writer = csv.DictWriter(f, fieldnames=CSV_FIELDS)
        writer.writeheader()
        writer.writerows(all_rows)

    print(f"Saved -> {OUTPUT_PATH}")


if __name__ == "__main__":
    main()
