import os
import json
import logging
from pathlib import Path
import time
TOKEN = os.getenv("DISCORD_TOKEN")
ADMIN_USER_ID = int(os.getenv("ADMIN_USER_ID"))
ADMIN_CHANNEL_ID = int(os.getenv("ADMIN_CHANNEL_ID"))
SERVER_ID = int(os.getenv("SERVER_ID"))
DEMOS_CHANNEL_ID = int(os.getenv("DEMOS_CHANNEL_ID"))
DATA_FILE = Path("servers.json")


with open("servers.json") as f:
    SERVERS = json.load(f)


def load_data() -> dict:
    if not DATA_FILE.exists():
        return {}
    with DATA_FILE.open("r", encoding="utf-8") as f:
        return json.load(f)



def save_data(data: dict):
    try:
        with DATA_FILE.open("w", encoding="utf-8") as f:
            json.dump(data, f, indent=2)

            # 🔥 wymusza fizyczny zapis na dysk
            f.flush()
            os.fsync(f.fileno())

        logging.info(f"✅ Dane zapisane do {DATA_FILE.read_text()}")
        time.sleep(3)
        logging.info(f"✅ Dane po 3s: {DATA_FILE.read_text()}")
        logging.info(f"DATA FILE: {DATA_FILE.resolve()}")

    except TypeError as e:
        logging.exception("❌ JSON serialization error (złe dane?)")
        raise

    except OSError as e:
        logging.exception("❌ Błąd zapisu pliku (dysk / permissions)")
        raise

    except Exception as e:
        logging.exception("❌ Nieznany błąd podczas zapisu JSON")
        raise