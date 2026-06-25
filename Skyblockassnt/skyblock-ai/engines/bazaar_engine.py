def safe_float(value):
    try:
        return float(value)
    except (TypeError, ValueError):
        return 0.0


def get_products(bazaar_response: dict):
    if not isinstance(bazaar_response, dict):
        return {}

    if "products" in bazaar_response:
        return bazaar_response.get("products", {})

    if "json" in bazaar_response:
        return bazaar_response.get("json", {}).get("products", {})

    return {}


def clean_item_name(product_id: str):
    return str(product_id).replace("_", " ").title()


def get_profit_tier(item):
    spread = item.get("spread", 0)
    spread_percent = item.get("spread_percent", 0)
    liquidity = item.get("liquidity", 0)

    if spread <= 0:
        return "NONE"

    if spread >= 1000 and spread_percent >= 5 and liquidity >= 10000:
        return "ELITE"

    if spread >= 250 and spread_percent >= 3 and liquidity >= 5000:
        return "GREAT"

    if spread >= 50 and spread_percent >= 1 and liquidity >= 1000:
        return "GOOD"

    return "LOW"


def get_risk_label(item):
    liquidity = item.get("liquidity", 0)
    spread_percent = item.get("spread_percent", 0)

    if liquidity < 500:
        return "High Risk"

    if spread_percent > 25:
        return "Volatile"

    if liquidity > 10000:
        return "Stable"

    return "Medium Risk"


def parse_bazaar_products(bazaar_response: dict):
    products = get_products(bazaar_response)
    parsed = []

    for product_id, product in products.items():
        if not isinstance(product, dict):
            continue

        status = product.get("quick_status", {})

        buy_price = safe_float(status.get("buyPrice"))
        sell_price = safe_float(status.get("sellPrice"))
        buy_volume = safe_float(status.get("buyVolume"))
        sell_volume = safe_float(status.get("sellVolume"))

        spread = sell_price - buy_price
        spread_percent = (spread / buy_price * 100) if buy_price > 0 else 0
        liquidity = buy_volume + sell_volume
        score = spread * max(spread_percent, 0) * max(liquidity, 1)

        item = {
            "product_id": str(product_id),
            "name": clean_item_name(product_id),
            "buy_price": buy_price,
            "sell_price": sell_price,
            "spread": spread,
            "spread_percent": spread_percent,
            "buy_volume": buy_volume,
            "sell_volume": sell_volume,
            "liquidity": liquidity,
            "score": score,
        }

        item["tier"] = get_profit_tier(item)
        item["risk"] = get_risk_label(item)

        parsed.append(item)

    return parsed


def get_top_flips(bazaar_response: dict, limit: int = 25):
    items = parse_bazaar_products(bazaar_response)
    flips = []

    for item in items:
        if item["buy_price"] <= 0 or item["sell_price"] <= 0:
            continue

        if item["spread"] <= 0:
            continue

        if item["liquidity"] < 500:
            continue

        flips.append(item)

    flips.sort(
        key=lambda x: (
            x["score"],
            x["spread"],
            x["liquidity"]
        ),
        reverse=True
    )

    return flips[:limit]


def search_bazaar(bazaar_response: dict, query="", limit: int = 50):
    items = parse_bazaar_products(bazaar_response)

    if query is None:
        query = ""

    query = str(query).lower().strip()

    if not query:
        return items[:limit]

    results = []

    for item in items:
        product_id = item.get("product_id", "").lower()
        name = item.get("name", "").lower()

        if query in product_id or query in name:
            results.append(item)

    return results[:limit]


def bazaar_items_to_table_rows(items):
    rows = []

    for item in items:
        rows.append({
            "Item": item.get("name", item.get("product_id", "UNKNOWN")),
            "Buy Price": f"{item.get('buy_price', 0):,.1f}",
            "Sell Price": f"{item.get('sell_price', 0):,.1f}",
            "Profit": f"{item.get('spread', 0):,.1f}",
            "Profit %": f"{item.get('spread_percent', 0):.2f}%",
            "Liquidity": f"{item.get('liquidity', 0):,.0f}",
            "Score": f"{item.get('score', 0):,.0f}",
            "Tier": item.get("tier", "NONE"),
            "Risk": item.get("risk", "Unknown"),
        })

    return rows


def format_bazaar_table(items):
    if not items:
        return "No Bazaar items found."

    lines = []

    for item in items:
        lines.append(
            f"{item.get('name', item.get('product_id', 'UNKNOWN'))}\n"
            f"  ID: {item.get('product_id', 'UNKNOWN')}\n"
            f"  Highest Buy Price: {item.get('buy_price', 0):,.1f}\n"
            f"  Lowest Sell Price: {item.get('sell_price', 0):,.1f}\n"
            f"  Margin: {item.get('spread', 0):,.1f} ({item.get('spread_percent', 0):.2f}%)\n"
            f"  Liquidity: {item.get('liquidity', 0):,.0f}\n"
            f"  Flip Score: {item.get('score', 0):,.0f}\n"
        )

    return "\n".join(lines)
