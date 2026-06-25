import json
import os
import requests


BASE_URL = "https://api.hypixel.net/v2"


def get_project_root() -> str:
    return os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


def load_config() -> dict:
    config_path = os.path.join(get_project_root(), "config", "config.json")

    with open(config_path, "r", encoding="utf-8") as file:
        return json.load(file)


def save_debug_json(filename: str, data: dict) -> str:
    cache_dir = os.path.join(get_project_root(), "cache")
    os.makedirs(cache_dir, exist_ok=True)

    file_path = os.path.join(cache_dir, filename)

    with open(file_path, "w", encoding="utf-8") as file:
        json.dump(data, file, indent=2)

    return file_path


def get_skyblock_profiles(uuid: str) -> dict:
    config = load_config()

    url = f"{BASE_URL}/skyblock/profiles"

    response = requests.get(
        url,
        params={"uuid": uuid},
        headers={"API-Key": config["api_key"]},
        timeout=20
    )

    data = {
        "endpoint": url,
        "params": {"uuid": uuid},
        "status_code": response.status_code,
        "ok": response.ok,
        "json": response.json() if response.text else {}
    }

    save_debug_json("last_skyblock_profiles.json", data)
    return data


def get_bazaar() -> dict:
    url = f"{BASE_URL}/skyblock/bazaar"

    response = requests.get(url, timeout=20)

    data = {
        "endpoint": url,
        "status_code": response.status_code,
        "ok": response.ok,
        "json": response.json() if response.text else {}
    }

    save_debug_json("last_bazaar.json", data)
    return data
