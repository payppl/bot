



async def get_server_status(server: dict) -> dict:

    server_type = server.get("type")

    if server_type == "cs2":
        from drivers.cs2_driver import get_cs2_status
        return await get_cs2_status(server)

    if server_type == "unturned":
        from managers.unturnedRconManager import get_unturned_status
        return await get_unturned_status(server)
    if server_type == "unturned_mod":
        from managers.unturnedRconManager import get_unturned_status
        return await get_unturned_status(server)

    raise ValueError(f"Unknown server type: {server_type}")

async def run_server_rcon(server: dict, command: str) -> str:

    server_type = server.get("type")

    if server_type == "cs2":
        from drivers.cs2_driver import run_cs2_rcon

        return await run_cs2_rcon(server, command)

    if server_type == "unturned":

        import logging
        from managers.unturnedRconManager import send_unturned_command

        logging.info(f"wywołuje komende {command}")
        return await send_unturned_command(server,command)

    if server_type == "unturned_mod":
        
        import logging
        from managers.unturnedRconManager import send_unturned_command

        logging.info(f"wywołuje komende {command}")
        return await send_unturned_command(server, command)

    raise Exception(f"RCON not supported for {server_type}")