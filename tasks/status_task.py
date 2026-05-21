import logging
from discord.ext import tasks
from jsonmanager.config import SERVERS
from drivers.driver_factory import get_server_status
from embedUI import build_embed


def start_status_task(bot):

    @tasks.loop(seconds=60)
    async def live_status():

        await bot.wait_until_ready()

        for name, server in SERVERS.items():

            try:

                channel = bot.get_channel(server["status_channel_id"])

                if not channel:
                    continue

                message = await channel.fetch_message(
                    server["status_message_id"]
                )

                data = await get_server_status(server)

                embed = build_embed(data,server)
                logging.info(f"pomyślnie zaktualizowałem serwer o nazwe: {name}")
                await message.edit(content=None, embed=embed)

            except Exception as e:
                print(f"STATUS ERROR ({name}):", e)

                continue

    live_status.start()