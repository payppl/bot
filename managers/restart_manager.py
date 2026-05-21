import asyncio
import logging
from drivers.driver_factory import run_server_rcon, get_server_status


async def graceful_restart(server):

    logging.info(f"Graceful restart for {server['type']}")

    data = await get_server_status(server)

    #if data["players"] > 0:
        #logging.info("Players joined — abort restart")
        #return


    # 🔥 1️⃣ broadcast
    await broadcast(server, "⚠️ Server restarting in 2 minutes!")

    await asyncio.sleep(60)

    await broadcast(server, "⚠️ Restart in 60 seconds!")

    await asyncio.sleep(50)

    await broadcast(server, "⚠️ Restart in 10 seconds!")

    await asyncio.sleep(10)

    # 🔥 2️⃣ docker restart
    container = server.get("container")

    if container:
        await asyncio.create_subprocess_shell(
            f"docker compose -f {container} restart"
)

async def broadcast(server, message):

    # tylko serwery z RCON!
    try:
        await run_server_rcon(server, f"say {message}")

    except Exception:
        logging.exception("Broadcast failed")