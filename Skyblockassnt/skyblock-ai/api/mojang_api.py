import requests


def get_uuid(username: str) -> dict:
    url = f"https://api.mojang.com/users/profiles/minecraft/{username}"

    response = requests.get(url, timeout=15)

    return {
        "url": url,
        "status_code": response.status_code,
        "ok": response.ok,
        "json": response.json() if response.text else {}
    }
