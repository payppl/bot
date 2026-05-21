import discord
from discord import app_commands
from discord.ext import commands
from jsonmanager.config import ADMIN_USER_ID,SERVER_ID
from jsonmanager.admins_config import grant_access, revoke_access


class permissions(commands.Cog):

    def __init__(self, bot: commands.Bot):
        self.bot = bot

        guild = discord.Object(id=SERVER_ID)

        # usuń jeśli istnieje
        if bot.tree.get_command("access", guild=guild):
            bot.tree.remove_command("access", guild=guild)

        self.group = app_commands.Group(
            name="access",
            description="Zarządzanie dostępem do bota"
        )
        # 🔥 TWORZYMY komendy ręcznie
        grant_cmd = app_commands.Command(
            name="grant",
            description="Nadaj dostęp",
            callback=self.grant
        )
        
        revoke_cmd = app_commands.Command(
            name="revoke",
            description="Zabierz dostęp",
            callback=self.revoke
        )

        # dodajemy do grupy
        self.group.add_command(grant_cmd)
        self.group.add_command(revoke_cmd)

        # rejestrujemy grupę
        bot.tree.add_command(self.group, guild=guild)


    async def grant(self,interaction: discord.Interaction, user: discord.User):
        if interaction.user.id != ADMIN_USER_ID:
            await interaction.response.send_message("❌ Brak uprawnień", ephemeral=True)
            return

        grant_access(user.id)
        await interaction.response.send_message(
            f"✅ {user.mention} ma teraz dostęp",
            ephemeral=True
        )


    async def revoke(self,interaction: discord.Interaction, user: discord.User):
        if interaction.user.id != ADMIN_USER_ID:
            await interaction.response.send_message("❌ Brak uprawnień", ephemeral=True)
            return

        revoke_access(user.id)
        await interaction.response.send_message(
            f"❌ {user.mention} stracił dostęp",
            ephemeral=True
        )

async def setup(bot: commands.Bot):
    await bot.add_cog(
        permissions(bot)
        )