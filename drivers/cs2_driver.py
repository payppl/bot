import os
import asyncio
import re
import logging
from rcon.source import Client


def offline_data():
    return {
        "online": False,
        "hostname": "SERVER CS2 OFFLINE",
        "map": "-",
        "players": 0,
        "max_players": 0
    }


async def get_cs2_status(server: dict) -> dict:

    password = os.getenv(server.get("env_password"))

    if not password:
        logging.error("CS2 DRIVER: Missing RCON password in .env")
        return offline_data()

    def run():
        with Client(
            server["host"],
            server["port"],
            passwd=password,
            timeout=10
        ) as client:
            return client.run("status")

    try:

        # 🔥 to_thread zapobiega blokowaniu event loopa
        text = await asyncio.to_thread(run)

        if not text:
            logging.warning("CS2 DRIVER: Empty response")
            return offline_data()

        return parse_cs2_status(text)

    except Exception as e:

        logging.exception(f"CS2 DRIVER ERROR ({server['host']}:{server['port']})")

        return offline_data()


def parse_cs2_status(text: str) -> dict:

    data = {
        "online": False,
        "hostname": "unknown",
        "map": "unknown",
        "players": 0,
        "max_players": 0
    }

    try:

        for line in text.splitlines():

            if ":" not in line:
                continue

            key, value = line.split(":", 1)

            key = key.strip().lower()
            value = value.strip()

            if key == "hostname":
                data["hostname"] = value
               
            elif key == "players":
                """
                Example:
                players : 3 humans, 0 bots (10 max)
                """
                # players : 3 humans, 0 bots (10 max)

                # aktualna liczba graczy
                players_match = re.search(r"^(\d+)", value)
                if players_match:
                    data["players"] = int(players_match.group(1))

                # max players (jeśli jest)
                max_match = re.search(r"\((\d+)\s*max\)", value)
                if max_match:
                    data["max_players"] = int(max_match.group(1))
                    

        # 🔥 fallback map parsing (CS2 ukrywa mapę w spawngroups)
        map_match = re.search(
            r"\[\d+:\s*([a-zA-Z0-9_]+)\s*\|\s*main lump",
            text
        )

        if map_match:
            data["map"] = map_match.group(1)
        data["online"] = True
        return data

    except Exception:
        logging.exception("CS2 PARSE ERROR")
        return offline_data()

async def run_cs2_rcon(server: dict, command: str) -> str:

    password = os.getenv(server.get("env_password"))

    if not password:
        raise Exception("Missing RCON password")

    def run():
        with Client(
            server["host"],
            server["port"],
            passwd=password,
            timeout=10
        ) as client:
            return client.run(command)

    return await asyncio.to_thread(run)