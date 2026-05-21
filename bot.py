import discord
import logging
import asyncio
import os
import docker
from pathlib import Path
from discord.ext import commands
from dotenv import load_dotenv


from embedUI import build_embed

from jsonmanager.config import TOKEN,SERVER_ID, SERVERS,DEMOS_CHANNEL_ID

#from managers.cs2manager import CS2Manager,start_http_server

from drivers.driver_factory import get_server_status
from drivers.driver_factory import run_server_rcon

from tasks.update_task import start_update_loop
from tasks.autorestart_taks import start_autorestart_loop
from tasks.status_task import start_status_task
from tasks.get_message_unt import start_chat_bridge

load_dotenv()
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s [%(levelname)s] %(message)s"
)
intents = discord.Intents.default()
intents.message_content = True
client = docker.from_env()



class MyBot(commands.Bot):

    async def setup_hook(self):
        
        start_status_task(self)
        await asyncio.sleep(10)
        #start_update_loop(self)
        await asyncio.sleep(10)
        start_autorestart_loop(self)
        start_chat_bridge(self)
        guild = discord.Object(id=SERVER_ID)
        self.tree.clear_commands(guild=guild)

        for file in os.listdir("./cogs"):
            if(file.endswith(".py")):
                await self.load_extension(f"cogs.{file[:-3]}")

        await self.tree.sync(guild=guild)


bot = MyBot(command_prefix="/", intents=intents)


@bot.event
async def on_ready():
    
    logging.info(f"✅ Bot online jako {bot.user}")
    logging.info(f"Loaded servers: {list(SERVERS.keys())}")
    for container in client.containers.list():
        logging.info(container.name)

    #cs2_manager = CS2Manager(bot,DEMOS_CHANNEL_ID)

    #await start_http_server()
    #asyncio.create_task(cs2_manager.polling_loop())

bot.run(TOKEN)