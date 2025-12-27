import json
import os

BINDINGS_FILE = "bindings.json"

bindings = {}
scram_key = None

def load_bindings():
    global bindings, scram_key
    if os.path.exists(BINDINGS_FILE):
        with open(BINDINGS_FILE, "r") as f:
            data = json.load(f)
            bindings = data.get("bindings", {})
            scram_key = data.get("scram_key")
    else:
        bindings = {}
        scram_key = None

def save_bindings():
    global bindings, scram_key
    with open(BINDINGS_FILE, "w") as f:
        json.dump({"bindings": bindings, "scram_key": scram_key}, f)

def bind_macro(key, file_path):
    global bindings
    # Remove previous bindings for this file_path
    reverse_bindings = {v: k for k, v in bindings.items()}
    if file_path in reverse_bindings:
        old_key = reverse_bindings[file_path]
        del bindings[old_key]

    # Add new binding
    bindings[key] = file_path
    save_bindings()  # Persist to file

def unbind_macro(macro_path):
    reverse = {v: k for k, v in bindings.items()}
    if macro_path in reverse:
        del bindings[reverse[macro_path]]
        save_bindings()

def bind_scram(key):
    global scram_key
    scram_key = key
    save_bindings()

def unbind_scram():
    global scram_key
    scram_key = None
    save_bindings()
