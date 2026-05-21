import aiohttp
import asyncio
import logging



def build_unturned_url(server: dict, endpoint: str) -> str: 
    host = server["container"] # nazwa kontenera w docker network
    return f"http://{host}:5000/{endpoint.lstrip('/')}"

def build_headers() -> dict: 
    return {
        "Authorization": f"Bearer {ROCKET_TOKEN}"
    }


async def send_unturned_command(server:dict, command: str):

    try:
        async with aiohttp.ClientSession() as session:
            async with session.post(
                build_unturned_url(server, "command"),
                data=command,
                headers=build_headers()
            ) as resp:

                text = await resp.text()

                return {
                    "success": resp.status == 200,
                    "http_status": resp.status,
                    "command": command,
                    "status": text
                }

    except Exception as e:
        return {
            "success": False,
            "http_status": 0,
            "command": command,
            "status": str(e)
        }

async def get_unturned_messages(server: dict):

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                build_unturned_url(server, "message"),
                headers=build_headers()
            ) as resp:

                if resp.status != 200:
                    return []
                data = await resp.json()
                logging.info(data)
                return data

    except Exception as e:
        logging.error(f"[CHAT BRIDGE ERROR] {e}")
        return []

async def get_unturned_status(server: dict):
    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(
                build_unturned_url(server, "status"),
                headers=build_headers()
            ) as resp:

                if resp.status != 200:
                    raise Exception(f"HTTP {resp.status}")

                text = await resp.text()

        # Parsowanie plain-text odpowiedzi
        lines = text.splitlines()
        data = {}

        for line in lines:
            if ":" in line:
                key, value = line.split(":", 1)
                data[key.strip()] = value.strip()

        players_current, players_max = data.get("Players", "0/0").split("/")

        return {
            "online": True,
            "hostname": data.get("Hostname", server['host']),
            "map": data.get("Map", "-"),
            "players": int(players_current),
            "max_players": int(players_max),
            "version": data.get("Version", "-"),
            "uptime": data.get("Uptime", "-"),
            "player_list": data.get("PlayerList", "")
        }

    except Exception as e:
        logging.error(f"[STATUS HTTP ERROR] {e}")
        return {
            "online": False,
            "hostname": "SERVER OFFLINE",
            "map": "-",
            "players": 0,
            "max_players": 0,
            "version": "-",
            "uptime": "-",
            "player_list": ""
        }