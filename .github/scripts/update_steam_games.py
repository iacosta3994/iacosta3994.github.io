"""Refresh games.json from Blits_Zen's public Steam library, or from the API."""

import json
import os
import urllib.request
import xml.etree.ElementTree as ET
from datetime import datetime, timezone
from pathlib import Path

STEAM_ID = "76561198204886037"
VANITY = "Blits_Zen"
OUT = Path(__file__).resolve().parents[2] / "games.json"
TOP = 12
UA = "Mozilla/5.0 (compatible; blizen-site/1.0)"


def fetch(url):
    request = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(request, timeout=30) as response:
        return response.read()


def from_xml(raw):
    if raw.lstrip().startswith(b"<"):
        root = ET.fromstring(raw)
    else:
        return []
    games = []
    for node in root.iter("game"):
        name = (node.findtext("name") or "").strip()
        appid = (node.findtext("appID") or "").strip()
        hours = node.findtext("hoursOnRecord") or "0"
        if not name:
            continue
        try:
            hours_n = float(hours)
        except ValueError:
            hours_n = 0
        if hours_n <= 0:
            continue
        games.append({"name": name, "appid": int(appid) if appid.isdigit() else None, "hours": round(hours_n, 1)})
    return games


def from_api(key):
    url = (
        "https://api.steampowered.com/IPlayerService/GetOwnedGames/v0001/"
        f"?key={key}&steamid={STEAM_ID}&format=json"
        "&include_appinfo=1&include_played_free_games=1"
    )
    payload = json.loads(fetch(url))
    games = []
    for game in payload.get("response", {}).get("games", []):
        minutes = game.get("playtime_forever") or 0
        if minutes <= 0 or not game.get("name"):
            continue
        games.append(
            {
                "name": game["name"],
                "appid": game.get("appid"),
                "hours": round(minutes / 60, 1),
            }
        )
    return games


def main():
    games = []
    for url in (
        f"https://steamcommunity.com/profiles/{STEAM_ID}/games?tab=all&xml=1",
        f"https://steamcommunity.com/id/{VANITY}/games?tab=all&xml=1",
    ):
        try:
            games = from_xml(fetch(url))
        except Exception as error:
            print(f"public list skipped: {error}")
            games = []
        if games:
            break

    key = os.environ.get("STEAM_API_KEY", "").strip()
    if not games and key:
        try:
            games = from_api(key)
        except Exception as error:
            print(f"api list skipped: {error}")
            games = []

    if not games:
        print("no public playtime yet; leaving games.json alone")
        return

    games.sort(key=lambda game: game["hours"], reverse=True)
    picked = []
    for game in games[:TOP]:
        hours = game["hours"]
        if hours >= 10:
            hours = round(hours)
        picked.append({**game, "hours": hours})

    document = {
        "updated": datetime.now(timezone.utc).strftime("%Y-%m-%dT%H:%M:%SZ"),
        "source": "steam",
        "games": picked,
    }
    OUT.write_text(json.dumps(document, indent=2) + "\n", encoding="utf-8")
    print(f"wrote {len(picked)} games")


if __name__ == "__main__":
    main()
