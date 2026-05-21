import discord
import asyncio
import logging
from discord.ext import commands
from discord import app_commands
from jsonmanager.config import SERVER_ID,SERVERS, save_data, load_data
from utils import admin_check
from embedUI import build_embed
from drivers.driver_factory import get_server_status


class botserver(commands.Cog):
    def __init__(self, bot: commands.Bot):
        self.bot = bot

        self.group = app_commands.Group(
            name="botserver",
            description="komendy serwera"
        )
        self.group.add_command(self.createembed)
        bot.tree.add_command(
            self.group,
            guild=discord.Object(id=SERVER_ID)
        )
    @app_commands.check(admin_check)
    @app_commands.command(   
        name="createembed",
        description="Tworzy embed z informacją o serwerze"
    )
    async def createembed(self,interaction: discord.Interaction,server_name: str):

        await interaction.response.defer(ephemeral=True)

        server = SERVERS.get(server_name)

        if not server:
            await interaction.followup.send("❌ Nieznany serwer", ephemeral=True)
            return
        try:
            data = await asyncio.wait_for(
                get_server_status(server),
                timeout=15
            )
            embed = build_embed(data, server)
            message = await interaction.channel.send(embed=embed)

            data_json = load_data()

            data_json[server_name]["status_message_id"] = message.id
            data_json[server_name]["status_channel_id"] = interaction.channel.id
            save_data(data_json)

        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Timeout podczas pobierania statusu", ephemeral=True)


        except Exception:
            logging.exception(f"STATUS COMMAND ERROR ({server_name})")
            await interaction.followup.send("🔥 Nie udało się pobrać statusu serwera", ephemeral=True)
            raise


async def setup(bot: commands.Bot):
    await bot.add_cog(
        botserver(bot)
        )