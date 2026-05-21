import discord
from discord import app_commands
from discord.ext import commands
from jsonmanager.restart_storage import load_schedule, save_schedule
from jsonmanager.config import SERVERS, SERVER_ID
from utils import admin_check

class autorestart(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        guild = discord.Object(id=SERVER_ID)

        # usuń jeśli istnieje
        if bot.tree.get_command("autorestart", guild=guild):
            bot.tree.remove_command("autorestart", guild=guild)

        self.group = app_commands.Group(
            name="autorestart",
            description="Zarządzanie auto restartem"
        )
        # 🔥 TWORZYMY komendy ręcznie
        start_cmd = app_commands.Command(
            name="start",
            description="Ustaw auto restart",
            callback=self.start
        )
        
        stop_cmd = app_commands.Command(
            name="stop",
            description="Wyłącz auto restart",
            callback=self.stop
        )

        list_cmd = app_commands.Command(
            name="list",
            description="Lista restartów",
            callback=self.list
        )

        start_cmd.add_check(admin_check)
        stop_cmd.add_check(admin_check)
        # dodajemy do grupy
        self.group.add_command(start_cmd)
        self.group.add_command(stop_cmd)
        self.group.add_command(list_cmd)

        # rejestrujemy grupę
        bot.tree.add_command(self.group, guild=guild)

    # --- CALLBACKI (bez dekoratorów!) ---

    async def start(
        self,
        interaction: discord.Interaction,
        server: str,
        hour: int,
        minute: int
    ):
        if server not in SERVERS:
            await interaction.response.send_message("Nieznany serwer", ephemeral=True)
            return

        if hour < 0 or hour > 23 or minute < 0 or minute > 59:
            await interaction.response.send_message("Niepoprawna godzina", ephemeral=True)
            return

        schedule = load_schedule()

        schedule[server] = {
            "hour": hour,
            "minute": minute
        }
        schedule[server]["enabled"] = True
        save_schedule(schedule)

        await interaction.response.send_message(
            f"Auto restart dla **{server}** ustawiony na {hour:02d}:{minute:02d}"
        )


    async def stop(
        self,
        interaction: discord.Interaction,
        server: str
    ):
        if server not in SERVERS:
            await interaction.response.send_message(
                "Nieznany serwer",
                ephemeral=True
            )
            return

        schedule = load_schedule()

        if server not in schedule:
            await interaction.response.send_message(
                f"Auto restart dla **{server}** nie jest ustawiony.",
                ephemeral=True
            )
            return

        # 🔥 usuń restart
        schedule[server]["enabled"] = False
        save_schedule(schedule)

        await interaction.response.send_message(
            f"Auto restart dla **{server}** został wyłączony."
        )


    async def list(
        self,
        interaction: discord.Interaction
    ):
        schedule = load_schedule()

        if not schedule:
            await interaction.response.send_message(
                "Brak ustawionych auto restartów."
            )
            return

        msg = "**Ustawione auto restarty:**\n"

        for server, time_data in schedule.items():
            msg += f"• {server} → {time_data['hour']:02d}:{time_data['minute']:02d}\n"

        await interaction.response.send_message(msg)



async def setup(bot):
    await bot.add_cog(autorestart(bot))