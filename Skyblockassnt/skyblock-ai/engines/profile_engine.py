import base64
import gzip
import io

SKILL_XP_TABLE = [
    50, 125, 200, 300, 500,
    750, 1000, 1500, 2000, 3500,
    5000, 7500, 10000, 15000, 20000,
    30000, 50000, 75000, 100000, 200000,
    300000, 400000, 500000, 600000, 700000,
    800000, 900000, 1000000, 1100000, 1200000,
    1300000, 1400000, 1500000, 1600000, 1700000,
    1800000, 1900000, 2000000, 2100000, 2200000,
    2300000, 2400000, 2500000, 2600000, 2750000,
    2900000, 3100000, 3400000, 3700000, 4000000,
    4300000, 4600000, 4900000, 5200000, 5500000,
    5800000, 6100000, 6400000, 6700000, 7000000
]


def xp_to_level(xp: float, max_level: int = 60) -> int:
    remaining = xp
    level = 0

    for required_xp in SKILL_XP_TABLE[:max_level]:
        if remaining >= required_xp:
            remaining -= required_xp
            level += 1
        else:
            break

    return level


def get_selected_profile(profile_response: dict):
    profiles = profile_response.get("json", {}).get("profiles", [])

    if not profiles:
        return None

    for profile in profiles:
        if profile.get("selected"):
            return profile

    return profiles[0]


def get_member(profile: dict, uuid: str):
    return profile.get("members", {}).get(uuid, {})


def get_skill_level(member: dict, skill_name: str):
    xp = (
        member
        .get("player_data", {})
        .get("experience", {})
        .get(f"SKILL_{skill_name.upper()}", 0)
    )

    return xp_to_level(xp)


def get_personal_bank(member: dict):
    profile_data = member.get("profile", {})
    bank = profile_data.get("bank_account", 0)

    if isinstance(bank, (int, float)):
        return round(bank), "member.profile.bank_account"

    return 0, "not found"


def get_magical_power(member: dict):
    accessory_bag = member.get("accessory_bag_storage", {})
    mp = accessory_bag.get("highest_magical_power", 0)

    if isinstance(mp, (int, float)):
        return int(mp)

    return 0


def normalize_id(value):
    return str(value).upper().replace(" ", "_").replace("-", "_").replace("'", "")


def decode_hypixel_nbt(data_string):
    if not data_string:
        return []

    try:
        import nbtlib
    except ImportError:
        print("Missing nbtlib. Run: pip install nbtlib")
        return []

    try:
        raw = base64.b64decode(data_string)
        decompressed = gzip.decompress(raw)

        nbt_file = nbtlib.File.parse(
            fileobj=io.BytesIO(decompressed)
        )

        items = nbt_file.get("i", [])
        return items

    except Exception as error:
        print("NBT decode error:", error)
        return []


def extract_item_id(item):
    try:
        tag = item.get("tag", {})
        extra = tag.get("ExtraAttributes", {})
        item_id = extra.get("id")

        if item_id:
            return normalize_id(item_id)

    except Exception:
        pass

    return None


def get_talisman_bag_data(member: dict):
    return (
        member
        .get("inventory", {})
        .get("bag_contents", {})
        .get("talisman_bag", {})
        .get("data")
    )


def get_owned_accessories_from_member(member: dict):
    data = get_talisman_bag_data(member)
    items = decode_hypixel_nbt(data)

    owned = []

    for item in items:
        item_id = extract_item_id(item)

        if item_id:
            owned.append(item_id)

    return sorted(set(owned))


def get_accessory_count(member: dict):
    owned = get_owned_accessories_from_member(member)
    return len(owned)


def parse_profile_stats(profile_response: dict, uuid: str, ign: str):
    profile = get_selected_profile(profile_response)

    if profile is None:
        return {
            "ign": ign,
            "profile_name": "None",
            "combat": "N/A",
            "mining": "N/A",
            "farming": "N/A",
            "foraging": "N/A",
            "fishing": "N/A",
            "enchanting": "N/A",
            "alchemy": "N/A",
            "catacombs": "N/A",
            "purse": 0,
            "bank": 0,
            "total_visible_coins": 0,
            "magical_power": 0,
            "accessories_count": 0,
            "owned_accessories": [],
            "bank_debug": "No profile found",
            "notes": "No SkyBlock profiles found."
        }

    member = get_member(profile, uuid)

    purse = member.get("currencies", {}).get("coin_purse", 0)
    bank, bank_path = get_personal_bank(member)

    dungeons = member.get("dungeons", {})
    dungeon_types = dungeons.get("dungeon_types", {})
    catacombs_xp = dungeon_types.get("catacombs", {}).get("experience", 0)

    total_visible = purse + bank

    magical_power = get_magical_power(member)
    owned_accessories = get_owned_accessories_from_member(member)
    accessories_count = len(owned_accessories)

    return {
        "ign": ign,
        "profile_name": profile.get("cute_name", "Unknown"),

        "combat": get_skill_level(member, "combat"),
        "mining": get_skill_level(member, "mining"),
        "farming": get_skill_level(member, "farming"),
        "foraging": get_skill_level(member, "foraging"),
        "fishing": get_skill_level(member, "fishing"),
        "enchanting": get_skill_level(member, "enchanting"),
        "alchemy": get_skill_level(member, "alchemy"),

        "catacombs": xp_to_level(catacombs_xp, max_level=50),

        "purse": round(purse),
        "bank": bank,
        "total_visible_coins": round(total_visible),

        "magical_power": magical_power,
        "accessories_count": accessories_count,
        "owned_accessories": owned_accessories,

        "bank_debug": bank_path,

        "notes": "Skill levels, MP, and accessory count are calculated from Hypixel API data."
    }