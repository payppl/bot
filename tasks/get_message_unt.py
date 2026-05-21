from discord.ext import tasks
import logging
from managers.unturnedRconManager import get_unturned_messages
from jsonmanager.config import SERVERS

def start_chat_bridge(bot):

    @tasks.loop(seconds=5)
    async def chat_loop():

        for server_name, server in SERVERS.items():
            if server.get("type") == "cs2":
                continue
            try:
                messages = await get_unturned_messages(server)

                if not messages:
                    continue
                
                channel_id = server.get("messages_channel_id")

                if not channel_id:
                    logging.warning(f"[CHAT BRIDGE] {server_name} nie ma messages_channel_id")
                    continue
                channel = bot.get_channel(channel_id)
                if channel is None:
                    try:
                        channel = await bot.fetch_channel(channel_id)
                    except Exception as e:
                        logging.error(
                            f"[CHAT BRIDGE] Nie znaleziono kanału {channel_id} dla {server_name}: {e}"
                        )
                        continue

                for entry in messages:
                    nick = entry["Nick"]
                    text = entry["Message"]
                    await channel.send(f"**{nick}**: {text}")
            except Exception as e:
                logging.exception(f"[CHAT BRIDGE ERROR] {server_name}: {e}")


    @chat_loop.before_loop
    async def before():
        await bot.wait_until_ready()

    chat_loop.start()
