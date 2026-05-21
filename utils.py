from jsonmanager.config import ADMIN_USER_ID, ADMIN_CHANNEL_ID
from jsonmanager.admins_config import has_access
import json

import discord
from discord import app_commands

async def owner_check(interaction: discord.Interaction):
    return interaction.user.id == ADMIN_USER_ID

async def admin_check(interaction: discord.Interaction):
    return has_access(interaction.user.id)