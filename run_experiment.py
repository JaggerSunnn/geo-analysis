#!/usr/bin/env python3
"""
GEO Analysis: Clothing E-commerce Experiment
Based on: Chen et al. (2026) "Navigating the Shift: A Comparative Analysis of
Web Search and Generative AI Response Generation"

Measures Claude's citation behavior across:
  1. Source typology (Brand / Earned / Social)
  2. Query intent (Informational / Consideration / Transactional)
  3. Source diversity and domain frequency
  4. Comparison baseline vs. paper's Google figures
"""

import os, re, json, time, sys
from collections import defaultdict
from urllib.parse import urlparse
from pathlib import Path
import anthropic

# Load .env from the same directory as this script (fallback to system env)
try:
    from dotenv import load_dotenv
    load_dotenv(Path(__file__).parent / ".env")
except ImportError:
    pass  # dotenv optional; system env vars still work

# ─────────────────────────────────────────────
# 50 CLOTHING E-COMMERCE QUERIES  (17 / 17 / 16)
# ─────────────────────────────────────────────

QUERIES = {
    "informational": [
        "What are the most popular women's clothing brands globally?",
        "How does fast fashion impact the environment?",
        "What clothing styles are trending this season?",
        "How to measure clothing size for online shopping?",
        "What is the brand history of ZARA in fashion?",
        "How do clothing subscription boxes work?",
        "What are the best sustainable clothing brands?",
        "How does dropshipping work for clothing e-commerce?",
        "What is the difference between fast fashion and slow fashion?",
        "How to identify high quality clothing materials online?",
        "What are the best brands for athletic wear?",
        "How do clothing size charts differ between countries?",
        "What is vintage clothing and where to buy it online?",
        "How do fashion designers create seasonal collections?",
        "What fabrics are best for summer clothing?",
        "How does clothing care labeling work internationally?",
        "What is the global market size for online fashion retail?",
    ],
    "consideration": [
        "Best affordable women's dresses under $50 online",
        "Top 10 online clothing stores for men's fashion",
        "Best sustainable clothing brands for eco-conscious shoppers",
        "Most reliable online clothing stores with free returns",
        "Best plus-size clothing brands online",
        "Top athletic wear brands compared by experts",
        "Best luxury fashion brands worth the price",
        "Most popular streetwear brands ranked this year",
        "Best online stores for children's clothing",
        "Top-rated work clothing brands for professionals",
        "Best budget fashion apps for clothing deals",
        "Most recommended online brands for winter coats",
        "Best online vintage clothing stores reviewed",
        "Top maternity clothing brands recommended",
        "Best online stores for wedding guest dresses",
        "Most popular Korean fashion brands for international buyers",
        "Best activewear brands for yoga and fitness",
    ],
    "transactional": [
        "Buy ZARA women's summer dress online free shipping",
        "H&M men's jeans sale buy now discount",
        "Nike women's running shoes order online best price",
        "Levi's 501 original jeans purchase online cheapest",
        "SHEIN clothing order tracking and express delivery",
        "ASOS next day delivery women's clothing purchase",
        "Uniqlo online store order international shipping",
        "Amazon fashion women's clothing prime deals buy",
        "Forever 21 online clearance sale buy now",
        "Nordstrom rack clothing sale online purchase",
        "Buy authentic designer handbags online discount",
        "Adidas originals clothing official store buy",
        "Gap factory outlet online sale purchase",
        "Mango women's clothing online order Europe",
        "Urban Outfitters clothing clearance sale buy",
        "PrettyLittleThing express delivery clothing order",
    ],
}

# ─────────────────────────────────────────────
# DOMAIN CLASSIFICATION RULES
# ─────────────────────────────────────────────

SOCIAL_DOMAINS = {
    "reddit.com", "twitter.com", "x.com", "instagram.com", "facebook.com",
    "tiktok.com", "pinterest.com", "tumblr.com", "youtube.com", "quora.com",
    "weibo.com", "xiaohongshu.com", "threads.net",
}

BRAND_DOMAINS = {
    "zara.com", "hm.com", "nike.com", "adidas.com", "shein.com", "asos.com",
    "uniqlo.com", "gap.com", "forever21.com", "nordstrom.com", "amazon.com",
    "levis.com", "mango.com", "urbanoutfitters.com", "prettylittlething.com",
    "macys.com", "target.com", "walmart.com", "abercrombie.com", "ae.com",
    "anthropologie.com", "freepeople.com", "express.com", "jcrew.com",
    "bananarepublic.com", "ralphlauren.com", "calvinklein.com", "tommyhilfiger.com",
    "coach.com", "katespade.com", "michaelkors.com", "guess.com", "lululemon.com",
    "underarmour.com", "puma.com", "newbalance.com", "vans.com", "converse.com",
    "reebok.com", "champion.com", "patagonia.com", "columbia.com", "thenorthface.com",
    "allbirds.com", "everlane.com", "reformation.com", "eileen-fisher.com",
    "farfetch.com", "net-a-porter.com", "matchesfashion.com", "ssense.com",
    "revolve.com", "shopbop.com", "bloomingdales.com", "saksfifthavenue.com",
    "zalando.com", "boohoo.com", "missguided.com", "fashionnova.com",
    "romwe.com", "zaful.com", "modcloth.com", "threadup.com",
    "poshmark.com", "depop.com", "ebay.com", "etsy.com", "shopify.com",
    "aliexpress.com", "taobao.com", "tmall.com", "jd.com",
}


def classify_domain(domain: str) -> str:
    d = domain.lower().lstrip("www.")
    if d in SOCIAL_DOMAINS:
        return "Social"
    if d in BRAND_DOMAINS:
        return "Brand"
    return "Earned"


def extract_domains(text: str) -> list[str]:
    pattern = r"https?://(?:www\.)?([a-zA-Z0-9\-]+(?:\.[a-zA-Z0-9\-]+)+)"
    raw = re.findall(pattern, text)
    # Also catch bare domain mentions like "example.com"
    bare = re.findall(r"\b(?:www\.)?([a-zA-Z0-9\-]+\.(?:com|org|net|io|co|fashion|style))\b", text)
    all_domains = list({d.lower() for d in raw + bare})
    return all_domains


# ─────────────────────────────────────────────
# EXPERIMENT RUNNER
# ─────────────────────────────────────────────

SYSTEM_PROMPT = (
    "You are an expert in clothing e-commerce and fashion retail. "
    "When answering questions, always cite specific websites, brand URLs, "
    "review platforms, or community sources to support your answer. "
    "Include multiple source types: brand official sites, independent review "
    "outlets, fashion media, and community forums. Provide full URLs where possible."
)


def run_experiment(api_key: str | None = None) -> list[dict]:
    client = anthropic.Anthropic(api_key=api_key or os.environ.get("ANTHROPIC_API_KEY"))
    results = []
    queries_flat = [(intent, q) for intent, qs in QUERIES.items() for q in qs]

    print(f"\n{'='*65}")
    print(f"  GEO CLOTHING E-COMMERCE EXPERIMENT — {len(queries_flat)} queries")
    print(f"{'='*65}\n")

    for idx, (intent, query) in enumerate(queries_flat, 1):
        label = f"[{idx:02d}/{len(queries_flat)}] [{intent[:5].upper()}]"
        print(f"{label} {query[:58]}...")

        try:
            msg = client.messages.create(
                model="claude-sonnet-4-6",
                max_tokens=800,
                system=SYSTEM_PROMPT,
                messages=[{"role": "user", "content": query}],
            )
            text = msg.content[0].text
            domains = extract_domains(text)
            types = [classify_domain(d) for d in domains]

            results.append({
                "query": query,
                "intent": intent,
                "response": text,
                "domains": domains,
                "source_types": types,
                "brand": types.count("Brand"),
                "earned": types.count("Earned"),
                "social": types.count("Social"),
                "total": len(domains),
            })
        except Exception as exc:
            print(f"  !! ERROR: {exc}")
            results.append({"query": query, "intent": intent, "error": str(exc)})

        time.sleep(0.3)

    return results


# ─────────────────────────────────────────────
# ANALYSIS
# ─────────────────────────────────────────────

def analyze(results: list[dict]) -> dict:
    valid = [r for r in results if "domains" in r]
    domain_freq: dict[str, int] = defaultdict(int)

    by_intent: dict[str, dict] = {}
    for intent in ("informational", "consideration", "transactional"):
        subset = [r for r in valid if r["intent"] == intent]
        total = sum(r["total"] for r in subset)
        brand = sum(r["brand"] for r in subset)
        earned = sum(r["earned"] for r in subset)
        social = sum(r["social"] for r in subset)
        by_intent[intent] = {
            "n": len(subset),
            "avg_sources": round(total / len(subset), 2) if subset else 0,
            "brand_pct": round(brand / total * 100, 1) if total else 0,
            "earned_pct": round(earned / total * 100, 1) if total else 0,
            "social_pct": round(social / total * 100, 1) if total else 0,
            "brand": brand, "earned": earned, "social": social, "total": total,
        }

    all_total = sum(r["total"] for r in valid)
    all_brand = sum(r["brand"] for r in valid)
    all_earned = sum(r["earned"] for r in valid)
    all_social = sum(r["social"] for r in valid)

    for r in valid:
        for d in r["domains"]:
            domain_freq[d] += 1

    top_domains = sorted(domain_freq.items(), key=lambda x: x[1], reverse=True)[:25]

    return {
        "total_queries": len(results),
        "valid_queries": len(valid),
        "overall": {
            "total": all_total,
            "brand_pct": round(all_brand / all_total * 100, 1) if all_total else 0,
            "earned_pct": round(all_earned / all_total * 100, 1) if all_total else 0,
            "social_pct": round(all_social / all_total * 100, 1) if all_total else 0,
        },
        "by_intent": by_intent,
        "unique_domains": len(domain_freq),
        "top_domains": [{"domain": d, "count": c, "type": classify_domain(d)} for d, c in top_domains],
    }


# ─────────────────────────────────────────────
# REPORT PRINTER
# ─────────────────────────────────────────────

GOOGLE_PAPER_BASELINE = {"brand_pct": 25.7, "earned_pct": 40.7, "social_pct": 33.6}

PAPER_CLAUDE_BASELINE = {
    "informational": {"brand_pct": 40.5, "earned_pct": 57.8, "social_pct": 1.7},
    "consideration":  {"brand_pct": 12.7, "earned_pct": 85.9, "social_pct": 1.5},
    "transactional":  {"brand_pct": 52.0, "earned_pct": 48.0, "social_pct": 0.0},
}


def print_report(analysis: dict) -> None:
    sep = "─" * 65
    print(f"\n{'='*65}")
    print("  GEO ANALYSIS REPORT — CLOTHING E-COMMERCE")
    print(f"  Model: claude-sonnet-4-6   Date: {time.strftime('%Y-%m-%d')}")
    print(f"{'='*65}\n")

    print(f"  Queries run   : {analysis['total_queries']}")
    print(f"  Valid results : {analysis['valid_queries']}")
    print(f"  Unique domains: {analysis['unique_domains']}")

    # ── OVERALL ────────────────────────────────────────────────
    o = analysis["overall"]
    g = GOOGLE_PAPER_BASELINE
    print(f"\n{sep}")
    print("  OVERALL SOURCE TYPOLOGY (all intents combined)")
    print(sep)
    print(f"  {'':20}  {'Brand':>8}  {'Earned':>8}  {'Social':>8}")
    print(f"  {'This experiment':20}  {o['brand_pct']:>7.1f}%  {o['earned_pct']:>7.1f}%  {o['social_pct']:>7.1f}%")
    print(f"  {'Paper: Claude baseline':20}  {'34.4%':>8}  {'64.5%':>8}  {'1.1%':>8}")
    print(f"  {'Paper: Google baseline':20}  {g['brand_pct']:>7.1f}%  {g['earned_pct']:>7.1f}%  {g['social_pct']:>7.1f}%")

    # ── BY INTENT ───────────────────────────────────────────────
    print(f"\n{sep}")
    print("  SOURCE TYPOLOGY BY QUERY INTENT")
    print(sep)
    print(f"  {'Intent':16}  {'N':>4}  {'Avg Src':>7}  {'Brand':>8}  {'Earned':>8}  {'Social':>8}")
    print(f"  {'-'*16}  {'----':>4}  {'-------':>7}  {'--------':>8}  {'--------':>8}  {'--------':>8}")
    for intent, s in analysis["by_intent"].items():
        pb = PAPER_CLAUDE_BASELINE.get(intent, {})
        print(f"  {intent:16}  {s['n']:>4}  {s['avg_sources']:>7.1f}  {s['brand_pct']:>7.1f}%  {s['earned_pct']:>7.1f}%  {s['social_pct']:>7.1f}%")
        if pb:
            print(f"  {'  (paper Claude)':16}  {'':>4}  {'':>7}  {pb['brand_pct']:>7.1f}%  {pb['earned_pct']:>7.1f}%  {pb['social_pct']:>7.1f}%")

    # ── TOP DOMAINS ─────────────────────────────────────────────
    print(f"\n{sep}")
    print("  TOP 25 MOST CITED DOMAINS")
    print(sep)
    print(f"  {'Type':7}  {'Cited':>5}  Domain")
    for item in analysis["top_domains"]:
        print(f"  {item['type']:7}  {item['count']:>5}x  {item['domain']}")

    print(f"\n{'='*65}\n")


# ─────────────────────────────────────────────
# MAIN
# ─────────────────────────────────────────────

if __name__ == "__main__":
    results = run_experiment()
    analysis = analyze(results)
    print_report(analysis)

    out_path = os.path.join(os.path.dirname(__file__), "geo_results.json")
    with open(out_path, "w", encoding="utf-8") as f:
        json.dump({"analysis": analysis, "raw": results}, f, indent=2, ensure_ascii=False, default=str)
    print(f"  Full results saved → {out_path}\n")
