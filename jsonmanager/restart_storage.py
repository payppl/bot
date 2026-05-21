import json
import os
import logging
from pathlib import Path
res_file = Path("restart_schedule.json")

with open("restart_schedule.json") as f:
    restartschedule = json.load(f)


def load_schedule():
    if not os.path.exists(res_file):
        return {}
    with open(res_file, "r") as f:
        return json.load(f)

def save_schedule(data):
    try:
        with open(res_file, "w") as f:
            json.dump(data, f, indent=2)
            f.flush()
            os.fsync(f.fileno())

    except TypeError as e:
        logging.exception("❌ JSON serialization error (złe dane?)")
        raise

    except OSError as e:
        logging.exception("❌ Błąd zapisu pliku (dysk / permissions)")
        raise

    except Exception as e:
        logging.exception("❌ Nieznany błąd podczas zapisu JSON")
        raise