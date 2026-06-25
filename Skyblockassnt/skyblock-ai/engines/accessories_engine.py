from data.accessories_database import ACCESSORIES_DATABASE
STARTER_ACCESSORIES = ACCESSORIES_DATABASE


RARITY_ORDER = {
    "COMMON": 1,
    "UNCOMMON": 2,
    "RARE": 3,
    "EPIC": 4,
    "LEGENDARY": 5,
    "MYTHIC": 6,
    "SPECIAL": 7,
    "VERY_SPECIAL": 8,
}


def normalize_id(value):
    return str(value).upper().replace(" ", "_").replace("-", "_").replace("'", "")


def get_stat_number(data, keys, default=0):
    if not isinstance(data, dict):
        return default

    for key in keys:
        value = data.get(key)

        if isinstance(value, (int, float)):
            return value

        if isinstance(value, str):
            try:
                return float(value)
            except ValueError:
                pass

    return default


def extract_owned_accessory_ids(profile_data):
    owned = set()

    if not isinstance(profile_data, dict):
        return owned

    possible_lists = [
        profile_data.get("accessories"),
        profile_data.get("accessory_bag"),
        profile_data.get("talismans"),
        profile_data.get("owned_accessories"),
        profile_data.get("owned_talismans"),
        profile_data.get("missing_accessories"),
    ]

    for accessories in possible_lists:
        if not isinstance(accessories, list):
            continue

        for accessory in accessories:
            if isinstance(accessory, dict):
                item_id = (
                    accessory.get("id")
                    or accessory.get("item_id")
                    or accessory.get("tag")
                    or accessory.get("internal_name")
                    or accessory.get("name")
                )

                if item_id:
                    owned.add(normalize_id(item_id))

            elif isinstance(accessory, str):
                owned.add(normalize_id(accessory))

    return owned


def calculate_magical_power(owned_ids=None, accessory_list=None, profile_data=None):
    if profile_data:
        real_mp = get_stat_number(
            profile_data,
            [
                "magical_power",
                "magic_power",
                "mp",
                "accessory_magical_power",
                "talisman_power",
            ],
            default=0
        )

        if real_mp:
            return int(real_mp)

    if owned_ids is None:
        owned_ids = set()

    if accessory_list is None:
        accessory_list = STARTER_ACCESSORIES

    total = 0

    for accessory in accessory_list:
        if normalize_id(accessory["id"]) in owned_ids:
            total += accessory.get("mp", 0)

    return total


def get_owned_accessories(profile_data, accessory_list=None):
    if accessory_list is None:
        accessory_list = STARTER_ACCESSORIES

    owned_ids = extract_owned_accessory_ids(profile_data)

    owned = []

    for accessory in accessory_list:
        if normalize_id(accessory["id"]) in owned_ids:
            owned.append({
                **accessory,
                "priority": get_priority_score(accessory),
            })

    return owned


def get_missing_accessories(profile_data, accessory_list=None):
    if accessory_list is None:
        accessory_list = STARTER_ACCESSORIES

    owned_ids = extract_owned_accessory_ids(profile_data)

    missing = []

    for accessory in accessory_list:
        accessory_id = normalize_id(accessory["id"])

        if accessory_id not in owned_ids:
            missing.append({
                **accessory,
                "priority": get_priority_score(accessory),
            })

    missing.sort(
        key=lambda x: (
            x.get("priority", 0),
            x.get("mp", 0),
            RARITY_ORDER.get(x.get("rarity", "COMMON"), 0),
        ),
        reverse=True
    )

    return missing


def get_accessory_summary(profile_data):
    owned_ids = extract_owned_accessory_ids(profile_data)
    owned = get_owned_accessories(profile_data)
    missing = get_missing_accessories(profile_data)

    real_mp = calculate_magical_power(
        owned_ids=owned_ids,
        profile_data=profile_data
    )

    real_owned_count = get_stat_number(
        profile_data,
        [
            "accessories_count",
            "owned_accessories_count",
            "talisman_count",
            "unique_accessories",
        ],
        default=len(owned)
    )

    return {
        "magical_power": int(real_mp),
        "owned_count": int(real_owned_count),
        "missing_count": len(missing),
        "owned": owned,
        "missing": missing,
    }


def get_priority_score(accessory):
    mp = accessory.get("mp", 0)
    rarity = RARITY_ORDER.get(accessory.get("rarity", "COMMON"), 1)

    return mp * 10 + rarity


def search_accessories(accessories, query=""):
    if query is None:
        query = ""

    query = str(query).lower().strip()

    if not query:
        return accessories

    return [
        accessory for accessory in accessories
        if query in accessory.get("name", "").lower()
        or query in accessory.get("id", "").lower()
        or query in accessory.get("rarity", "").lower()
        or query in accessory.get("source", "").lower()
    ]


def format_price(value):
    if value is None:
        return "Unknown"

    try:
        value = int(value)
    except (TypeError, ValueError):
        return "Unknown"

    if value >= 1_000_000:
        return f"{value / 1_000_000:.1f}M"

    if value >= 1_000:
        return f"{value / 1_000:.1f}K"

    return str(value)


def get_coins_per_mp(accessory):
    price = accessory.get("estimated_price")
    mp = accessory.get("mp", 0)

    if price is None or mp <= 0:
        return None

    return int(price / mp)


def accessories_to_table_rows(accessories):
    rows = []

    for accessory in accessories:
        price = accessory.get("estimated_price")
        coins_per_mp = get_coins_per_mp(accessory)

        rows.append({
            "Name": accessory.get("name", "Unknown"),
            "Rarity": accessory.get("rarity", "UNKNOWN"),
            "MP": str(accessory.get("mp", 0)),
            "Price": format_price(price),
            "Coins/MP": format_price(coins_per_mp),
            "Source": accessory.get("source", "Unknown"),
            "Priority": str(accessory.get("priority", 0)),
        })

    return rows