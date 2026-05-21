import json
import os

PERMISSIONS_FILE = "Admins.json"

def ensure_file():
    if not os.path.exists(PERMISSIONS_FILE):
        with open(PERMISSIONS_FILE, "w") as f:
            json.dump({"allowed_users": []}, f, indent=4)

def load_permissions():
    ensure_file()
    with open(PERMISSIONS_FILE, "r") as f:
        return json.load(f)

def save_permissions(data):
    with open(PERMISSIONS_FILE, "w") as f:
        json.dump(data, f, indent=4)

def has_access(user_id: int):
    data = load_permissions()
    return user_id in data["allowed_users"]

def grant_access(user_id: int):
    data = load_permissions()
    if user_id not in data["allowed_users"]:
        data["allowed_users"].append(user_id)
        save_permissions(data)

def revoke_access(user_id: int):
    data = load_permissions()
    if user_id in data["allowed_users"]:
        data["allowed_users"].remove(user_id)
        save_permissions(data)