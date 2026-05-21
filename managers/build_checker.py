import aiohttp
import logging


async def fetch_buildid(appid: int):

    url = f"https://api.steamcmd.net/v1/info/{appid}"

    try:

        async with aiohttp.ClientSession() as session:
            async with session.get(url) as res:

                data = await res.json()

                return int(
                    data["data"][str(appid)]["depots"]["branches"]["public"]["buildid"]
                )

    except Exception:
        logging.exception("Failed to fetch buildid")
        return None
