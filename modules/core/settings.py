import json
import customtkinter as ctk
import os

SETTINGS_FILE = "settings.json"

theme = "System"
replay_mode = "once"
replay_count = 1

def load_settings():
    global theme, replay_mode, replay_count
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                theme = data.get("theme", "System")
                replay_mode = data.get("replay_mode", "once")
                replay_count = data.get("replay_count", 1)
        except:
            pass

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({"theme": theme, "replay_mode": replay_mode, "replay_count": replay_count}, f)
        ctk.set_appearance_mode(theme)
    except:
        pass

def reset_settings():
    global theme, replay_mode, replay_count
    theme = "System"
    replay_mode = "once"
    replay_count = 1
    save_settings()