import json
import re
from pathlib import Path

import requests


ITEMS_URL = "https://api.hypixel.net/v2/resources/skyblock/items"
AUCTIONS_URL = "https://api.hypixel.net/v2/skyblock/auctions"

OUTPUT_FILE = Path(__file__).parent / "accessories_database.py"

INCLUDE_AUCTION_PRICES = True


MP_BY_RARITY = {
    "COMMON": 3,
    "UNCOMMON": 5,
    "RARE": 8,
    "EPIC": 12,
    "LEGENDARY": 16,
    "MYTHIC": 22,
    "DIVINE": 22,
    "SPECIAL": 3,
    "VERY_SPECIAL": 5,
}


def clean_name(name):
    if not name:
        return ""

    name = re.sub(r"§.", "", str(name))
    name = name.replace("✪", "").strip()
    return " ".join(name.split())


def normalize_name(name):
    return clean_name(name).lower()


def infer_family(item_id):
    item_id = str(item_id).upper()

    suffixes = [
        "_TALISMAN",
        "_RING",
        "_ARTIFACT",
        "_RELIC",
        "_BELT",
        "_CLOAK",
        "_NECKLACE",
        "_BRACELET",
        "_BADGE",
        "_ORB",
        "_CORE",
    ]

    family = item_id

    for suffix in suffixes:
        if family.endswith(suffix):
            family = family[: -len(suffix)]
            break

    family = re.sub(r"_[0-9]+$", "", family)

    return family


def get_items():
    response = requests.get(ITEMS_URL, timeout=30)
    response.raise_for_status()
    data = response.json()

    if not data.get("success"):
        raise RuntimeError("Hypixel items API did not return success.")

    return data.get("items", [])


def is_accessory(item):
    category = str(item.get("category", "")).upper()
    return category == "ACCESSORY"


def get_lowest_bin_prices():
    prices = {}

    try:
        first = requests.get(AUCTIONS_URL, params={"page": 0}, timeout=30)
        first.raise_for_status()
        first_data = first.json()

        total_pages = int(first_data.get("totalPages", 0))

        for page in range(total_pages):
            data = first_data if page == 0 else requests.get(
                AUCTIONS_URL,
                params={"page": page},
                timeout=30
            ).json()

            for auction in data.get("auctions", []):
                if not auction.get("bin"):
                    continue

                name = normalize_name(auction.get("item_name", ""))
                price = auction.get("starting_bid", 0)

                if not name or not isinstance(price, (int, float)):
                    continue

                if name not in prices or price < prices[name]:
                    prices[name] = int(price)

    except Exception as error:
        print("Auction price scan failed:", error)

    return prices


def build_database():
    items = get_items()
    lowest_bins = get_lowest_bin_prices() if INCLUDE_AUCTION_PRICES else {}

    accessories = []

    for item in items:
        if not is_accessory(item):
            continue

        item_id = item.get("id")
        name = clean_name(item.get("name"))
        rarity = str(item.get("tier", "COMMON")).upper()

        if not item_id or not name:
            continue

        price = lowest_bins.get(normalize_name(name))

        accessories.append({
            "id": item_id,
            "name": name,
            "rarity": rarity,
            "mp": MP_BY_RARITY.get(rarity, 0),
            "family": infer_family(item_id),
            "source": "Unknown",
            "estimated_price": price,
            "category": item.get("category", "ACCESSORY"),
        })

    accessories.sort(key=lambda x: (x["family"], x["rarity"], x["name"]))

    return accessories


def write_python_database(accessories):
    content = "ACCESSORIES_DATABASE = "
    content += json.dumps(accessories, indent=4)
    content += "\n"

    OUTPUT_FILE.write_text(content, encoding="utf-8")


if __name__ == "__main__":
    accessories = build_database()
    write_python_database(accessories)

    print(f"Generated {len(accessories)} accessories.")
    print(f"Saved to {OUTPUT_FILE}")