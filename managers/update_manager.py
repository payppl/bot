import asyncio
import logging
import discord
from managers.build_checker import fetch_buildid
from drivers.driver_factory import get_server_status
from managers.restart_manager import graceful_restart
from jsonmanager.config import save_data, load_data

async def send_update_alert(bot, server, name):
    data_json = load_data()
    channel_id = data_json[name]["update_channel_id"]

    if not channel_id:
        logging.info("nie podano id kanału")
        return

    try:
        channel = await bot.fetch_channel(channel_id)

        embed = discord.Embed(
            title="🚨 Server Update Detected",
            description=f"**{server['type'].upper()}** is updating now.",
            color=0xf1c40f
        )

        embed.add_field(
            name="Action",
            value="Server will restart automatically.",
            inline=False
        )

        await channel.send(embed=embed)

    except Exception:
        logging.exception("Failed to send update alert")

async def smart_update_check(bot, server,name):
    data_json = load_data()
    server_id = data_json[name]        # np. "cs2", "unturned"
    appid = server["appid"]

    latest_build = await fetch_buildid(appid)
    if not latest_build:
        return False

    current_build = server_id["buildid"]

    # 🔥 pierwszy run – zapisz build i NIE updateuj
    if current_build == 0:
        server_id["buildid"] = latest_build
        save_data(data_json)
        logging.info(f"[{server_id}] Initial build saved: {latest_build}")
        return False

    if latest_build == current_build:
        logging.info(f"[{server_id}] No update (build {latest_build})")
        return False

    # 🔥 UPDATE WYKRYTY
    logging.info(
        f"[{server_id}] UPDATE DETECTED {current_build} → {latest_build}"
    )

    await send_update_alert(bot, server, name)

    # 🔒 player safety
    data = await get_server_status(server)
    if data["players"] > 0:
        logging.info(f"[{server_id}] Players online – delaying update")
        return False

    # 🔥 steamcmd
    await run_steam_update(server)

    # 🔥 restart
    await graceful_restart(server)

    # 🔥 zapisz nowy build
    server_id["buildid"] = latest_build
    save_data(data_json)
    
    return True

async def run_steam_update(server):

    appid = server["appid"]
    #zrobić to pod docker compose (unt, cs2) update