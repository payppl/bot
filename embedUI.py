import discord
import datetime
from discord.ui import View, Button
def player_bar(players, max_players):

    if max_players == 0:
        return "0/0"

    filled = int((players / max_players) * 10)

    return "█" * filled + "░" * (10 - filled) + f" {players}/{max_players}"


def build_embed(data, server):
    
    online = data["online"] != False

    color = get_server_color(
        data["players"],
        data["max_players"],
        online
    )
    icon = "🟢" if online else "🔴"
    host = server["host"]
    port = server["port"]
    embed = discord.Embed(
        title=f"{icon} {data['hostname']}",
        color=color
    )

    embed.add_field(
        name="🗺️ Mapa",
        value=data["map"],
        inline=True
    )

    embed.add_field(
        name="👥 Gracze",
        value=player_bar(data["players"], data["max_players"]),
        inline=False
    )
    if data.get("version"):
        embed.add_field(
            name="📦 Wersja serwera",
            value=data["version"],
            inline=False
        )
    if data.get("uptime"):
        embed.add_field(
            name="⌛ Serwer działa przez: ",
            value=data["uptime"],
            inline=False
        )
    if data.get("online") == True:
        embed.add_field(
            name="Dołącz na serwer!",
            value=f"👉**lub połącz się: {host} port {port}**",
            inline=False
        )

    embed.set_footer(text="Automatyczne odświeżanie co 60 sekund!")

    return embed

def get_server_color(players: int, max_players: int, online: bool):

    if not online:
        return 0x2c2f33  # ciemny szary (Discord style)

    if max_players == 0:
        return 0x95a5a6  # fallback szary

    fill = players / max_players

    if fill == 0:
        return 0x3498db  # 🔵 blue

    elif fill < 0.5:
        return 0x2ecc71  # 🟢 green

    elif fill < 0.8:
        return 0xf1c40f  # 🟡 yellow

    elif fill < 1:
        return 0xe67e22  # 🟠 orange

    else:
        return 0xe74c3c  # 🔴 red

def build_unturned_command_embed(data: dict, user) -> discord.Embed:
    success = data.get("status") == "OK"

    embed = discord.Embed(
        title="Komenda wykonana" if success else "Błąd komendy",
        colour=0x00F51D if success else 0xFF0000,
        timestamp=datetime.datetime.now()
    )
    embed.add_field(
        name="🛠 Komenda",
        value=f"```{data.get('command', '-')}```",
        inline=False
    )

    embed.add_field(
        name="📡 Status",
        value=f"```{data.get('status', '-')} | {data.get('http_status', '-')}```",
        inline=False
    )
#dopisać kto wysyłał komende
    embed.set_footer(
        text=f"BulletLand.pl | wykonywał {user}",
    )

    return embed