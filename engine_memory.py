import json
import os
from config import MEMORY_FILE

def load_memory():
    if not os.path.exists(MEMORY_FILE):
        # Default memory if file doesn't exist
        return {"name": "User", "college": "B.Tech", "last_project": "None"}
    with open(MEMORY_FILE, "r") as f:
        return json.load(f)

def save_memory(data):
    with open(MEMORY_FILE, "w") as f:
        json.dump(data, f, indent=4)
    return "Memory updated."

def update_user_info(key, value):
    memory = load_memory()
    memory[key] = value
    save_memory(memory)
    return f"I've remembered your {key} is {value}."