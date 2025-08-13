import random
import string
import json

STORAGE_FILE = "storage.json"

def load_data():
    with open(STORAGE_FILE, "r") as f:
        return json.load(f)

def save_data(data):
    with open(STORAGE_FILE, "w") as f:
        json.dump(data, f, indent=4)

def generate_key(days: int):
    key = ''.join(random.choices(string.ascii_uppercase + string.digits, k=10))
    data = load_data()
    data["premium_keys"][key] = days
    save_data(data)
    return key
