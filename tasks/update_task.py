import asyncio
import logging
from discord.ext import tasks
from jsonmanager.config import SERVERS
from managers.update_manager import smart_update_check

def start_update_loop(bot):

    @tasks.loop(minutes=30)
    async def update_loop():

        for name, server in SERVERS.items():

            try:

                logging.info(f"Checking updates for {name}...")

                await smart_update_check(bot, server, name)

                # 🔥 stagger — NIE usuwaj tego
                await asyncio.sleep(120)

            except Exception:
                logging.exception(f"Update crash for {name}")


    # 🔥 MEGA WAŻNE (bot cache)
    @update_loop.before_loop
    async def before_loop():
        await bot.wait_until_ready()
        logging.info("Update loop started")


    update_loop.start()