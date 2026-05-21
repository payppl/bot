import discord
import asyncio
import logging
from discord.ext import commands
from discord import app_commands
from jsonmanager.config import SERVER_ID,SERVERS, save_data, load_data
from utils import admin_check
from embedUI import build_embed,build_unturned_command_embed
from drivers.driver_factory import get_server_status,run_server_rcon

class utils(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        guild = discord.Object(id=SERVER_ID)

        # usuń jeśli istnieje
        if bot.tree.get_command("utils", guild=guild):
            bot.tree.remove_command("utils", guild=guild)

        self.group = app_commands.Group(
            name="utils",
            description="Zarządzanie auto restartem"
        )
        # 🔥 TWORZYMY komendy ręcznie
        servers_cmd = app_commands.Command(
            name="servers",
            description="Lista serwerów",
            callback=self.servers
        )
        
        fullclear_cmd = app_commands.Command(
            name="fullclear",
            description="Czyści cały chat",
            callback=self.fullclear
        )

        rcon_cmd = app_commands.Command(
            name="rcon",
            description="komendy rcona do serwerów",
            callback=self.rcon
        )
        status_cmd = app_commands.Command(
            name="status",
            description="Status wybranego serwera",
            callback=self.status
        )

        servers_cmd.add_check(admin_check)
        fullclear_cmd.add_check(admin_check)
        rcon_cmd.add_check(admin_check)
        status_cmd.add_check(admin_check)
        # dodajemy do grupy
        self.group.add_command(status_cmd)
        self.group.add_command(fullclear_cmd)
        self.group.add_command(rcon_cmd)
        self.group.add_command(servers_cmd)
        # rejestrujemy grupę
        bot.tree.add_command(self.group, guild=guild)


    async def servers(self,interaction: discord.Interaction):
        await interaction.channel.send(
            "**Dostępne serwery:**\n" +
            "\n".join(f"👉 {name}" for name in SERVERS.keys())
        )

    async def fullclear(self,interaction: discord.Interaction):
        async for msg in ctx.channel.history(limit=None):
            try:
                await msg.delete()
            except Exception:
                pass
 
    async def status(self,interaction: discord.Interaction, servername: str):

        server = SERVERS.get(servername)
        if not server:
            await interaction.followup.send("❌ Nieznany serwer")
            return
        try:
            data = await asyncio.wait_for(
                get_server_status(server),
                timeout=15
            )

            await interaction.response.defer(thinking=True)
            embed = build_embed(data, server)
            await interaction.followup.send(embed=embed)

        except asyncio.TimeoutError:
            await interaction.followup.send("⏱️ Timeout podczas pobierania statusu")


        except Exception as e:
            logging.exception(f"STATUS COMMAND ERROR ({servername})")
            await interaction.followup.send("🔥 Nie udało się pobrać statusu serwera")

    async def rcon(self,interaction: discord.Interaction, server_name: str, *, command: str):

        BLOCKED = ["quit", "exit", "shutdown"]
        if any(b in command.lower() for b in BLOCKED):
            await interaction.channel.send("⛔ Komenda zablokowana")
            return

        server = SERVERS.get(server_name)

        if not server:
            logging.info("nieznany serwer")
            await interaction.channel.send("❌ Nieznany serwer")
            return
        
        try:
            logging.info(f"{server}: {command}")
            

            result = await run_server_rcon(server, command)

            if not result:
                result = "(brak odpowiedzi)"
                logging.info("brak odpowiedzi")
            
            if server_name == "unturned":
                embed = build_unturned_command_embed(result,interaction.user)
                await interaction.channel.send(embed=embed)
            else:
                await interaction.channel.send(f"```{result[:1900]}```")

        except Exception as e:
            logging.info(f"🔥 RCON error: {e}")
            await interaction.channel.send(f"🔥 RCON error: {e}")
            
   

async def setup(bot: commands.Bot):
    await bot.add_cog(utils(bot))


