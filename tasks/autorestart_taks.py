import asyncio
import datetime
import docker
import logging
from discord.ext import tasks
from jsonmanager.restart_storage import load_schedule,save_schedule
from drivers.driver_factory import get_server_status
from managers.restart_manager import broadcast
from jsonmanager.config import SERVERS
client = docker.from_env()

def start_autorestart_loop(bot):

    @tasks.loop(minutes=1)
    async def autorestart_loop():

        schedule = load_schedule()
        now = datetime.datetime.now()
        today = now.date().isoformat()

        current_hour = now.hour
        current_minute = now.minute
        
        for server_name, time_data in schedule.items():
            logging.info(f"[AutoRestart]: {server_name} : {time_data}")

            if not time_data.get("enabled", True):
                continue
            logging.info("[AutoRestart]: czekam na godzine restartu....")
  
            restart_time = time_data["hour"] * 60 + time_data["minute"]
            current_time = current_hour * 60 + current_minute
            logging.info(f"[AutoRestart]: {restart_time} : {current_time}")
            today = now.date().isoformat()
            if (current_time >= restart_time and time_data.get("last_run") != today):

                schedule[server_name]["last_run"] = today
                save_schedule(schedule)
                server = SERVERS[server_name]
                if not server:
                    continue
                # 🔥 Nie restartuj z graczami
                data = await get_server_status(server)
                if data["players"] > 0:
                    logging.info(f"{server_name} ma graczy — restart pominięty")
                    continue

                # 🔥 1️⃣ broadcast
                await broadcast(server, '" Server restarting in 2 minutes!"')

                await asyncio.sleep(60)

                await broadcast(server, '" Restart in 60 seconds!"')

                await asyncio.sleep(50)
                if server_name == "unturned":
                    from managers.unturnedRconManager import send_unturned_command
                    send_unturned_command(server,"save")
                    
                await broadcast(server, '" Restart in 10 seconds!"')

                await asyncio.sleep(30)
                container_name = server["container"]
                container = client.containers.get(container_name)
                try:
                    await asyncio.to_thread(container.restart)
                    logging.info("[AutoRestart]: restart zakończony")
                except Exception as e:
                    logging.error(f"[AutoRestart]: restart error {e}")

    @autorestart_loop.before_loop
    async def before():
        await bot.wait_until_ready()

    autorestart_loop.start()
