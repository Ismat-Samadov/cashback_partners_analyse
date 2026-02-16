"""
Generate business-insight charts for the Azerbaijan bank partner dataset.
Bolkart is the central focus; all other banks are benchmarks.

Output: charts/*.png  (10 charts)
"""

import csv
import os
from collections import Counter, defaultdict
from pathlib import Path

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt
import matplotlib.ticker as mticker
import numpy as np

# ── Paths ────────────────────────────────────────────────────────────────────
DATA_PATH = Path(__file__).parent.parent / "data" / "data.csv"
BOLKART_PATH = Path(__file__).parent.parent / "data" / "bolkart.csv"
CHARTS_DIR = Path(__file__).parent.parent / "charts"
CHARTS_DIR.mkdir(exist_ok=True)

# ── Palette ───────────────────────────────────────────────────────────────────
BOLKART_COLOR = "#E8382F"          # Bolkart red
ACCENT       = "#2A6EBB"           # comparison blue
GRAY         = "#9E9E9E"
LIGHT_GRAY   = "#E0E0E0"
POSITIVE     = "#2ECC71"

BANK_COLORS = {
    "bolkart":       BOLKART_COLOR,
    "birbank":       "#1565C0",
    "tamkart":       "#00838F",
    "rabitabank":    "#6A1B9A",
    "xalqbank":      "#2E7D32",
    "unibank":       "#E65100",
    "pashabank":     "#F9A825",
    "bankrespublika":"#546E7A",
}

BANK_LABELS = {
    "bolkart":       "Bolkart",
    "birbank":       "Birbank",
    "tamkart":       "TamKart",
    "rabitabank":    "Rabitabank",
    "xalqbank":      "XalqBank",
    "unibank":       "Unibank",
    "pashabank":     "PASHA Bank",
    "bankrespublika":"Bank Respublika",
}

plt.rcParams.update({
    "font.family":     "DejaVu Sans",
    "axes.spines.top": False,
    "axes.spines.right": False,
    "axes.grid":       True,
    "grid.alpha":      0.35,
    "grid.linestyle":  "--",
    "axes.titlesize":  13,
    "axes.labelsize":  11,
})


# ── Load data ─────────────────────────────────────────────────────────────────
def load() -> list[dict]:
    with open(DATA_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def load_bolkart_raw() -> list[dict]:
    with open(BOLKART_PATH, newline="", encoding="utf-8") as f:
        return list(csv.DictReader(f))


def save(fig: plt.Figure, name: str):
    path = CHARTS_DIR / name
    fig.savefig(path, dpi=150, bbox_inches="tight")
    plt.close(fig)
    print(f"  saved: {path.name}")


def cb_float(row: dict, field: str = "cashback") -> float | None:
    try:
        v = float(row[field])
        return v if v > 0 else None
    except (ValueError, KeyError):
        return None


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 1 – Partner Network Size by Bank
# ═══════════════════════════════════════════════════════════════════════════════
def chart_partner_counts(rows: list[dict]):
    src_order = ["birbank", "tamkart", "bolkart", "rabitabank",
                 "bankrespublika", "xalqbank", "unibank", "pashabank"]
    counts = Counter(r["source"] for r in rows)

    labels = [BANK_LABELS[s] for s in src_order]
    values = [counts[s] for s in src_order]
    colors = [BANK_COLORS[s] for s in src_order]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, values, color=colors, width=0.6, zorder=3)

    for bar, val in zip(bars, values):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 25,
                f"{val:,}", ha="center", va="bottom", fontsize=10, fontweight="bold")

    # Bolkart label emphasis
    bolkart_idx = src_order.index("bolkart")
    bars[bolkart_idx].set_edgecolor("black")
    bars[bolkart_idx].set_linewidth(1.8)

    ax.set_title("Partner Network Size by Bank", fontweight="bold", pad=14)
    ax.set_ylabel("Number of Partners")
    ax.set_ylim(0, max(values) * 1.18)
    ax.yaxis.set_major_formatter(mticker.FuncFormatter(lambda x, _: f"{int(x):,}"))
    ax.tick_params(axis="x", rotation=15)
    fig.tight_layout()
    save(fig, "01_partner_network_size.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 2 – Reward Strategy Mix by Bank (stacked bar)
# ═══════════════════════════════════════════════════════════════════════════════
def chart_reward_strategy(rows: list[dict]):
    src_order = ["bolkart", "birbank", "tamkart", "rabitabank",
                 "xalqbank", "unibank", "pashabank", "bankrespublika"]
    reward_colors = {
        "cashback":    "#2ECC71",
        "taksit_only": "#3498DB",
        "miles":       "#F39C12",
        "unknown":     LIGHT_GRAY,
    }
    reward_labels = {
        "cashback":    "Cashback",
        "taksit_only": "Taksit only",
        "miles":       "Miles",
        "unknown":     "No reward data",
    }

    rt_by_src = defaultdict(Counter)
    for r in rows:
        rt_by_src[r["source"]][r["reward_type"]] += 1

    totals = {s: sum(rt_by_src[s].values()) for s in src_order}
    pcts   = {s: {rt: rt_by_src[s][rt] / totals[s] * 100 for rt in reward_colors}
              for s in src_order}

    labels = [BANK_LABELS[s] for s in src_order]
    x = np.arange(len(src_order))
    width = 0.55

    fig, ax = plt.subplots(figsize=(12, 6))
    bottom = np.zeros(len(src_order))
    for rt, color in reward_colors.items():
        vals = [pcts[s][rt] for s in src_order]
        bars = ax.bar(x, vals, width, bottom=bottom, label=reward_labels[rt],
                      color=color, zorder=3)
        for i, (bar, v) in enumerate(zip(bars, vals)):
            if v > 6:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bottom[i] + v / 2,
                        f"{v:.0f}%", ha="center", va="center",
                        fontsize=8.5, color="white", fontweight="bold")
        bottom += np.array(vals)

    ax.set_xticks(x)
    ax.set_xticklabels(labels, rotation=15, ha="right")
    ax.set_ylabel("Share of Partners (%)")
    ax.set_ylim(0, 110)
    ax.set_title("Reward Strategy Mix by Bank", fontweight="bold", pad=14)
    ax.legend(loc="upper right", framealpha=0.85, fontsize=9)
    ax.grid(axis="y")
    ax.grid(axis="x", alpha=0)
    fig.tight_layout()
    save(fig, "02_reward_strategy_mix.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 3 – Bolkart: Partners by Category
# ═══════════════════════════════════════════════════════════════════════════════
def chart_bolkart_categories(rows: list[dict]):
    bolkart = [r for r in rows if r["source"] == "bolkart"]
    cat_count = Counter(r["category"] for r in bolkart if r["category"])
    top = cat_count.most_common(15)
    cats   = [c for c, _ in reversed(top)]
    counts = [n for _, n in reversed(top)]
    colors = [BOLKART_COLOR if i >= len(top) - 1 else "#EF9A9A" for i in range(len(top))]

    fig, ax = plt.subplots(figsize=(10, 7))
    bars = ax.barh(cats, counts, color=[BOLKART_COLOR if c > 100 else "#EF9A9A" for c in counts],
                   zorder=3)
    for bar, val in zip(bars, counts):
        ax.text(bar.get_width() + 2, bar.get_y() + bar.get_height() / 2,
                str(val), va="center", fontsize=9, fontweight="bold")

    ax.set_xlabel("Number of Partners")
    ax.set_title("Bolkart — Partner Distribution by Category (Top 15)", fontweight="bold", pad=14)
    ax.set_xlim(0, max(counts) * 1.15)
    ax.grid(axis="x")
    ax.grid(axis="y", alpha=0)
    fig.tight_layout()
    save(fig, "03_bolkart_category_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 4 – Bolkart: Cashback Rate Distribution
# ═══════════════════════════════════════════════════════════════════════════════
def chart_bolkart_cashback_distribution(rows: list[dict]):
    bolkart = [r for r in rows if r["source"] == "bolkart"]
    cb_vals = {}
    for r in bolkart:
        v = cb_float(r)
        if v is not None:
            cb_vals[v] = cb_vals.get(v, 0) + 1

    sorted_vals = sorted(cb_vals.items())
    labels = [f"{v:.1f}%" for v, _ in sorted_vals]
    counts = [c for _, c in sorted_vals]
    colors = [BOLKART_COLOR if c >= 10 else "#EF9A9A" for c in counts]

    fig, ax = plt.subplots(figsize=(10, 5))
    bars = ax.bar(labels, counts, color=colors, zorder=3, width=0.6)
    for bar, val in zip(bars, counts):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.3,
                str(val), ha="center", va="bottom", fontsize=9, fontweight="bold")

    ax.set_xlabel("Cashback Rate")
    ax.set_ylabel("Number of Partners")
    ax.set_title("Bolkart — Cashback Rate Distribution (Partners with Cashback > 0)",
                 fontweight="bold", pad=14)
    ax.set_ylim(0, max(counts) * 1.2)
    fig.tight_layout()
    save(fig, "04_bolkart_cashback_distribution.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 5 – Average Cashback Rate Comparison (banks with cashback)
# ═══════════════════════════════════════════════════════════════════════════════
def chart_avg_cashback_comparison(rows: list[dict]):
    sources = ["bolkart", "birbank", "rabitabank", "xalqbank", "unibank"]

    stats = {}
    for src in sources:
        vals = [cb_float(r) for r in rows if r["source"] == src]
        vals = [v for v in vals if v is not None]
        if vals:
            stats[src] = {
                "avg": sum(vals) / len(vals),
                "max": max(vals),
                "n":   len(vals),
            }

    src_order = sorted(stats, key=lambda s: -stats[s]["avg"])
    labels = [BANK_LABELS[s] for s in src_order]
    avgs   = [stats[s]["avg"] for s in src_order]
    maxes  = [stats[s]["max"] for s in src_order]
    colors = [BANK_COLORS[s] for s in src_order]

    x = np.arange(len(src_order))
    width = 0.38

    fig, ax = plt.subplots(figsize=(10, 5))
    bars_avg = ax.bar(x - width / 2, avgs,  width, label="Average Cashback %",
                      color=colors, zorder=3)
    bars_max = ax.bar(x + width / 2, maxes, width, label="Maximum Cashback %",
                      color=colors, alpha=0.45, zorder=3, hatch="//")

    for bar, val in zip(bars_avg, avgs):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{val:.1f}%", ha="center", va="bottom", fontsize=9, fontweight="bold")
    for bar, val in zip(bars_max, maxes):
        ax.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 0.2,
                f"{val:.0f}%", ha="center", va="bottom", fontsize=9, color=GRAY)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Cashback (%)")
    ax.set_title("Average & Maximum Cashback Rate — Bank Comparison",
                 fontweight="bold", pad=14)
    ax.legend(framealpha=0.85)
    ax.set_ylim(0, max(maxes) * 1.2)
    fig.tight_layout()
    save(fig, "05_avg_max_cashback_comparison.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 6 – Cashback Partner Count & Coverage Rate by Bank
# ═══════════════════════════════════════════════════════════════════════════════
def chart_cashback_coverage(rows: list[dict]):
    sources = ["bolkart", "birbank", "tamkart", "rabitabank",
               "xalqbank", "unibank"]

    totals   = Counter(r["source"] for r in rows)
    cashback = Counter(r["source"] for r in rows if r["reward_type"] == "cashback")

    labels  = [BANK_LABELS[s] for s in sources]
    counts  = [cashback[s] for s in sources]
    pcts    = [cashback[s] / totals[s] * 100 for s in sources]
    colors  = [BANK_COLORS[s] for s in sources]

    fig, ax1 = plt.subplots(figsize=(11, 5))
    ax2 = ax1.twinx()

    x = np.arange(len(sources))
    w = 0.5
    bars = ax1.bar(x, counts, w, color=colors, zorder=3, label="# Cashback Partners")
    ax2.plot(x, pcts, "o--", color="black", linewidth=1.8, markersize=7,
             label="Cashback Coverage %", zorder=4)

    for bar, val in zip(bars, counts):
        ax1.text(bar.get_x() + bar.get_width() / 2, bar.get_height() + 5,
                 str(val), ha="center", va="bottom", fontsize=9, fontweight="bold")
    for xi, pct in zip(x, pcts):
        ax2.text(xi, pct + 1.5, f"{pct:.0f}%", ha="center", va="bottom",
                 fontsize=9, color="black")

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels, rotation=10)
    ax1.set_ylabel("Number of Cashback Partners")
    ax2.set_ylabel("Cashback Coverage Rate (%)")
    ax2.set_ylim(0, 115)
    ax1.set_ylim(0, max(counts) * 1.3)
    ax1.set_title("Cashback Partner Count & Coverage Rate by Bank",
                  fontweight="bold", pad=14)
    lines1, labels1 = ax1.get_legend_handles_labels()
    lines2, labels2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, labels1 + labels2, loc="upper right", framealpha=0.85)
    fig.tight_layout()
    save(fig, "06_cashback_coverage_by_bank.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 7 – Bolkart: Category Cashback Performance
# ═══════════════════════════════════════════════════════════════════════════════
def chart_bolkart_category_cashback(rows: list[dict]):
    bolkart = [r for r in rows if r["source"] == "bolkart"]
    cat_cb  = defaultdict(list)
    for r in bolkart:
        v = cb_float(r)
        if v is not None:
            cat_cb[r["category"]].append(v)

    # Sort by avg descending
    cat_stats = {cat: {"avg": sum(vals)/len(vals), "n": len(vals), "max": max(vals)}
                 for cat, vals in cat_cb.items()}
    ordered = sorted(cat_stats.items(), key=lambda x: -x[1]["avg"])

    cats   = [c for c, _ in ordered]
    avgs   = [cat_stats[c]["avg"] for c in cats]
    ns     = [cat_stats[c]["n"]   for c in cats]
    colors = [BOLKART_COLOR if a >= 6 else "#EF9A9A" for a in avgs]

    fig, ax = plt.subplots(figsize=(10, 6))
    bars = ax.barh(list(reversed(cats)), list(reversed(avgs)),
                   color=list(reversed(colors)), zorder=3)
    for bar, n, avg in zip(bars, reversed(ns), reversed(avgs)):
        ax.text(bar.get_width() + 0.1, bar.get_y() + bar.get_height() / 2,
                f"{avg:.1f}%  (n={n})", va="center", fontsize=8.5)

    ax.set_xlabel("Average Cashback (%)")
    ax.set_title("Bolkart — Average Cashback Rate by Category\n(Categories with at least one cashback partner)",
                 fontweight="bold", pad=14)
    ax.set_xlim(0, max(avgs) * 1.35)
    ax.grid(axis="x")
    ax.grid(axis="y", alpha=0)
    fig.tight_layout()
    save(fig, "07_bolkart_category_cashback_performance.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 8 – Taksit (Installment) Month Coverage Comparison
# ═══════════════════════════════════════════════════════════════════════════════
def chart_taksit_comparison(rows: list[dict]):
    sources = ["bolkart", "tamkart", "birbank", "unibank"]
    milestones = [3, 6, 12, 24]

    def has_month(r, m):
        return str(m) in r["taksit_months"].replace(";", ",").split(",") if r["taksit_months"] else False

    totals = Counter(r["source"] for r in rows)
    data   = {}
    for src in sources:
        src_rows = [r for r in rows if r["source"] == src and r["taksit_months"].strip()]
        data[src] = {m: sum(1 for r in src_rows if has_month(r, m)) for m in milestones}

    x      = np.arange(len(milestones))
    width  = 0.18
    offsets = np.linspace(-(len(sources)-1)/2, (len(sources)-1)/2, len(sources)) * width

    fig, ax = plt.subplots(figsize=(11, 5))
    for i, src in enumerate(sources):
        vals   = [data[src][m] for m in milestones]
        bars   = ax.bar(x + offsets[i], vals, width, label=BANK_LABELS[src],
                        color=BANK_COLORS[src], zorder=3)
        for bar, val in zip(bars, vals):
            if val > 0:
                ax.text(bar.get_x() + bar.get_width() / 2,
                        bar.get_height() + 4,
                        str(val), ha="center", va="bottom", fontsize=7.5)

    ax.set_xticks(x)
    ax.set_xticklabels([f"{m} months" for m in milestones])
    ax.set_ylabel("Number of Partners Offering Installment")
    ax.set_title("Installment (Taksit) Month Availability by Bank",
                 fontweight="bold", pad=14)
    ax.legend(framealpha=0.85)
    fig.tight_layout()
    save(fig, "08_taksit_month_comparison.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 9 – Bolkart Popularity Tier vs Cashback Offering
# ═══════════════════════════════════════════════════════════════════════════════
def chart_bolkart_popularity_cashback(raw_bolkart: list[dict]):
    tier_labels = {"1": "High Popularity", "2": "Mid Popularity", "3": "Standard"}
    tier_order  = ["1", "2", "3"]

    tier_data = defaultdict(lambda: {"total": 0, "with_cb": 0, "cb_vals": []})
    for r in raw_bolkart:
        t = r.get("popularity", "3")
        tier_data[t]["total"] += 1
        try:
            v = float(r["cashback"])
            if v > 0:
                tier_data[t]["with_cb"] += 1
                tier_data[t]["cb_vals"].append(v)
        except:
            pass

    labels    = [tier_labels[t] for t in tier_order]
    totals    = [tier_data[t]["total"]   for t in tier_order]
    with_cb   = [tier_data[t]["with_cb"] for t in tier_order]
    no_cb     = [tier_data[t]["total"] - tier_data[t]["with_cb"] for t in tier_order]
    avg_cb    = [sum(tier_data[t]["cb_vals"]) / len(tier_data[t]["cb_vals"])
                 if tier_data[t]["cb_vals"] else 0
                 for t in tier_order]

    x     = np.arange(len(tier_order))
    width = 0.4

    fig, ax1 = plt.subplots(figsize=(9, 5))
    ax2 = ax1.twinx()

    b1 = ax1.bar(x - width/2, no_cb,   width, label="No Cashback",   color=LIGHT_GRAY,   zorder=3)
    b2 = ax1.bar(x - width/2, with_cb, width, label="With Cashback", color=BOLKART_COLOR, zorder=3,
                 bottom=no_cb)
    ax2.plot(x + width/2, avg_cb, "D--", color=ACCENT, linewidth=1.8,
             markersize=8, label="Avg Cashback % (of cb partners)", zorder=4)

    for xi, tot, wcb, ac in zip(x, totals, with_cb, avg_cb):
        pct = wcb / tot * 100 if tot else 0
        ax1.text(xi - width/2, tot + 4, f"{pct:.0f}%", ha="center", fontsize=9, fontweight="bold")
        if ac:
            ax2.text(xi + width/2, ac + 0.3, f"{ac:.1f}%", ha="center", fontsize=9, color=ACCENT)

    ax1.set_xticks(x)
    ax1.set_xticklabels(labels)
    ax1.set_ylabel("Number of Partners")
    ax2.set_ylabel("Avg Cashback Rate (%)")
    ax2.set_ylim(0, 14)
    ax1.set_title("Bolkart — Popularity Tier vs Cashback Offering",
                  fontweight="bold", pad=14)
    lines1, lbls1 = ax1.get_legend_handles_labels()
    lines2, lbls2 = ax2.get_legend_handles_labels()
    ax1.legend(lines1 + lines2, lbls1 + lbls2, loc="upper right", framealpha=0.85)
    fig.tight_layout()
    save(fig, "09_bolkart_popularity_vs_cashback.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Chart 10 – Cross-Bank: Restaurants & Healthcare Cashback Comparison
# ═══════════════════════════════════════════════════════════════════════════════
def chart_category_cross_bank(rows: list[dict]):
    """
    Show avg cashback for two high-value categories across banks that have them.
    Restaurants / Cafes and Health / Medical — Bolkart highlighted.
    """
    RESTAURANT_KEYS = ["restoran", "kafe", "restaurant", "café", "рестор"]
    HEALTH_KEYS     = ["tibb", "sağlamlıq", "health", "klinik", "медицин", "seyhi"]

    def matches(cat: str, keys: list[str]) -> bool:
        cat_l = cat.lower()
        return any(k in cat_l for k in keys)

    sources = ["bolkart", "rabitabank", "xalqbank"]  # have both categories with cashback

    def avg_for(src, keys):
        vals = [cb_float(r) for r in rows
                if r["source"] == src
                and matches(r["category"], keys)
                and cb_float(r) is not None]
        vals = [v for v in vals if v]
        return (sum(vals) / len(vals), len(vals)) if vals else (0, 0)

    rest_data   = {s: avg_for(s, RESTAURANT_KEYS) for s in sources}
    health_data = {s: avg_for(s, HEALTH_KEYS)     for s in sources}

    labels = [BANK_LABELS[s] for s in sources]
    rest_avgs   = [rest_data[s][0]   for s in sources]
    rest_ns     = [rest_data[s][1]   for s in sources]
    health_avgs = [health_data[s][0] for s in sources]
    health_ns   = [health_data[s][1] for s in sources]

    x     = np.arange(len(sources))
    width = 0.35
    colors_main = [BANK_COLORS[s] for s in sources]
    colors_fade = [c + "88" for c in [BANK_COLORS[s] for s in sources]]   # transparent hex

    fig, ax = plt.subplots(figsize=(10, 5))
    b1 = ax.bar(x - width/2, rest_avgs,   width, label="Restaurants & Cafes",
                color=[BANK_COLORS[s] for s in sources], zorder=3)
    b2 = ax.bar(x + width/2, health_avgs, width, label="Health & Clinics",
                color=[BANK_COLORS[s] for s in sources], alpha=0.45, zorder=3, hatch="//")

    for xi, rv, rn, hv, hn in zip(x, rest_avgs, rest_ns, health_avgs, health_ns):
        if rv:
            ax.text(xi - width/2, rv + 0.15, f"{rv:.1f}%\n(n={rn})",
                    ha="center", va="bottom", fontsize=8.5, fontweight="bold")
        if hv:
            ax.text(xi + width/2, hv + 0.15, f"{hv:.1f}%\n(n={hn})",
                    ha="center", va="bottom", fontsize=8.5, color=GRAY)

    ax.set_xticks(x)
    ax.set_xticklabels(labels)
    ax.set_ylabel("Average Cashback (%)")
    ax.set_title("Restaurants & Health Category Cashback — Bank Comparison",
                 fontweight="bold", pad=14)
    ax.legend(framealpha=0.85)
    ax.set_ylim(0, max(rest_avgs + health_avgs) * 1.35)
    fig.tight_layout()
    save(fig, "10_category_cashback_cross_bank.png")


# ═══════════════════════════════════════════════════════════════════════════════
# Main
# ═══════════════════════════════════════════════════════════════════════════════
def main():
    print("Loading data ...")
    rows        = load()
    raw_bolkart = load_bolkart_raw()
    print(f"  {len(rows):,} total rows loaded\n")

    print("Generating charts:")
    chart_partner_counts(rows)
    chart_reward_strategy(rows)
    chart_bolkart_categories(rows)
    chart_bolkart_cashback_distribution(rows)
    chart_avg_cashback_comparison(rows)
    chart_cashback_coverage(rows)
    chart_bolkart_category_cashback(rows)
    chart_taksit_comparison(rows)
    chart_bolkart_popularity_cashback(raw_bolkart)
    chart_category_cross_bank(rows)

    print(f"\nAll charts saved to: {CHARTS_DIR}")


if __name__ == "__main__":
    main()
