import tkinter as tk
import customtkinter as ctk
import subprocess
import sys
import json
import os
import threading
from PIL import Image, ImageTk
from pynput import keyboard

def resource_path(relative_path):
    try:
        base_path = sys._MEIPASS
    except Exception:
        base_path = os.path.abspath(".")
    return os.path.join(base_path, relative_path)

ctk.set_appearance_mode("System")
ctk.set_default_color_theme("blue")

BINDINGS_FILE = "bindings.json"
SETTINGS_FILE = "settings.json"

file_path = None
bindings = {}
recording = False
listener = None
global_listener = None
scram_key = None
current_process = None
replay_mode = "once"  # once, count, infinite
replay_count = 1
theme = "System"  # System, Light, Dark
settings_window = None

def load_bindings():
    global bindings, scram_key
    if os.path.exists(BINDINGS_FILE):
        try:
            with open(BINDINGS_FILE, 'r') as f:
                data = json.load(f)
                bindings = data.get("bindings", {})
                scram_key = data.get("scram_key")
        except:
            bindings = {}
            scram_key = None

def save_bindings():
    try:
        with open(BINDINGS_FILE, 'w') as f:
            json.dump({"bindings": bindings, "scram_key": scram_key}, f)
    except:
        pass

def load_settings():
    global replay_mode, replay_count, theme
    if os.path.exists(SETTINGS_FILE):
        try:
            with open(SETTINGS_FILE, 'r') as f:
                data = json.load(f)
                replay_mode = data.get("replay_mode", "once")
                replay_count = data.get("replay_count", 1)
                theme = data.get("theme", "System")
        except:
            pass

def save_settings():
    try:
        with open(SETTINGS_FILE, 'w') as f:
            json.dump({"replay_mode": replay_mode, "replay_count": replay_count, "theme": theme}, f)
    except:
        pass

def wait_for_macro_end(process):
    process.wait()
    playing_label.pack_forget()
    enable_macro_buttons()
    global current_process
    current_process = None

def read_macro_operations(file_path):
    if not file_path:
        return []
    operations = []
    try:
        with open(file_path, 'r') as file:
            for line in file:
                line = line.strip()
                if not line:
                    continue
                operation = line.split(" ")[0]
                if operation in ["press", "delay", "setting", "click", "type"]:
                    operations.append(line)
    except:
        pass
    return operations

def display_operations():
    # Clear previous
    for widget in operations_scrollable.winfo_children():
        widget.destroy()
    
    if not file_path:
        no_macro_label = ctk.CTkLabel(operations_scrollable, text="No macro loaded")
        no_macro_label.pack(padx=10, pady=5)
        return
    
    operations = read_macro_operations(file_path)
    if not operations:
        no_ops_label = ctk.CTkLabel(operations_scrollable, text="No operations found")
        no_ops_label.pack(padx=10, pady=5)
        return
    
    for i, op in enumerate(operations, 1):
        op_label = ctk.CTkLabel(operations_scrollable, text=f"{i}. {op}", anchor="w")
        op_label.pack(fill="x", padx=10, pady=2)

def load_macro():
    global file_path
    file_path = tk.filedialog.askopenfilename(
        title="Select MacroTS File",
        filetypes=[("MacroTS files", "*.macrots"), ("All files", "*")]
    )
    if file_path:
        print(f"Selected file: {file_path}")
        bind_macro_button.pack(after=load_macro_button, padx=10, pady=10)
        update_bound_label()
        display_operations()
    else:
        bind_macro_button.pack_forget()
        update_bound_label()
        display_operations()

    return file_path

def bind_macro():
    global recording, listener
    if not file_path:
        print("No macro file selected.")
        return
    
    # Hide bound labels during recording
    bound_key_label.pack_forget()
    unbind_button.pack_forget()
    
    recording = True
    recording_label.pack(after=bind_macro_button, padx=10, pady=10)
    load_macro_button.configure(state="disabled")
    bind_macro_button.configure(state="disabled")
    cancel_button.pack(after=recording_label, padx=10, pady=10)
    
    def on_press(key):
        global recording
        if recording:
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            
            # Unbind previous key for this macro if any
            reverse_bindings = {v: k for k, v in bindings.items()}
            if file_path in reverse_bindings:
                old_k = reverse_bindings[file_path]
                del bindings[old_k]
            
            bindings[k] = file_path
            print(f"Bound {k} to {file_path}")
            stop_recording()
            update_bound_label()
            save_bindings()
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def stop_recording():
    global recording, listener
    recording = False
    recording_label.pack_forget()
    cancel_button.pack_forget()
    load_macro_button.configure(state="normal")
    bind_macro_button.configure(state="normal")
    if listener:
        listener.stop()
        listener = None
    update_bound_label()

def update_bound_label():
    if file_path:
        reverse_bindings = {v: k for k, v in bindings.items()}
        if file_path in reverse_bindings:
            key = reverse_bindings[file_path]
            bound_key_label.configure(text=f"Bound to: {key}")
            bound_key_label.pack(after=bind_macro_button, padx=10, pady=10)
            unbind_button.pack(after=bound_key_label, padx=10, pady=10)
        else:
            bound_key_label.configure(text="")
            bound_key_label.pack_forget()
            unbind_button.pack_forget()
    else:
        bound_key_label.configure(text="")
        bound_key_label.pack_forget()
        unbind_button.pack_forget()

def unbind_macro():
    if file_path:
        reverse_bindings = {v: k for k, v in bindings.items()}
        if file_path in reverse_bindings:
            key = reverse_bindings[file_path]
            del bindings[key]
            print(f"Unbound {key} from {file_path}")
            update_bound_label()
            save_bindings()

def bind_scram():
    global recording, listener
    # Hide bound labels during recording
    bound_key_label.pack_forget()
    unbind_button.pack_forget()
    
    recording = True
    load_macro_button.configure(state="disabled")
    bind_macro_button.configure(state="disabled")
    cancel_button.pack(after=recording_label, padx=10, pady=10)
    
    def on_press(key):
        global recording, scram_key
        if recording:
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            scram_key = k
            print(f"Bound scram to {k}")
            stop_recording()
            save_bindings()
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def disable_macro_buttons():
    load_macro_button.configure(state="disabled")
    bind_macro_button.configure(state="disabled")
    unbind_button.configure(state="disabled")

def enable_macro_buttons():
    load_macro_button.configure(state="normal")
    bind_macro_button.configure(state="normal")
    unbind_button.configure(state="normal")
    update_bound_label()

def on_global_press(key):
    global current_process
    run_macro_path = resource_path("run_macro.py")

    try:
        k = key.char
    except AttributeError:
        k = str(key)
    
    if k == scram_key:
        if current_process:
            current_process.terminate()
            current_process = None
            print("Macro terminated by scram key")
            enable_macro_buttons()
            playing_label.pack_forget()
    elif k in bindings:
        if replay_mode == "infinite":
            if current_process:
                current_process.terminate()
                current_process = None
                print("Macro stopped by pressing the key again")
                enable_macro_buttons()
                playing_label.pack_forget()
            else:
                disable_macro_buttons()
                playing_label.pack(after=title, padx=10, pady=5)
                current_process = subprocess.Popen([sys.executable, run_macro_path, bindings[k], "infinite"])
        elif replay_mode == "count":
            if current_process:
                current_process.terminate()
            disable_macro_buttons()
            playing_label.pack(after=title, padx=10, pady=5)
            current_process = subprocess.Popen([sys.executable, run_macro_path, bindings[k], "count", str(replay_count)])
            threading.Thread(target=wait_for_macro_end, args=(current_process,), daemon=True).start()
        else:  # once
            if current_process:
                current_process.terminate()
            disable_macro_buttons()
            playing_label.pack(after=title, padx=10, pady=5)
            current_process = subprocess.Popen([sys.executable, run_macro_path, bindings[k], "once"])
            threading.Thread(target=wait_for_macro_end, args=(current_process,), daemon=True).start()

def on_close():
    if global_listener:
        global_listener.stop()
    app.destroy()

def close_settings_window():
    global settings_window
    if settings_window:
        settings_window.grab_release()  # Release the modal grab
        settings_window.destroy()
        settings_window = None

def open_settings():
    global settings_window
    if settings_window is not None and settings_window.winfo_exists():
        settings_window.focus()  # Bring to front
        return
    settings_window = ctk.CTkToplevel(app)
    settings_window.title("Settings")
    settings_window.geometry("400x500")
    settings_window.resizable(False, False)
    settings_window.protocol("WM_DELETE_WINDOW", lambda: close_settings_window())
    settings_window.transient(app)  # Make it a child of the main window
    settings_window.grab_set()  # Make it modal
    
    # Scram section
    scram_frame = ctk.CTkFrame(settings_window)
    scram_frame.pack(pady=10, padx=10, fill="x")
    scram_title = ctk.CTkLabel(scram_frame, text="Scram Key", font=ctk.CTkFont(size=16, weight="bold"))
    scram_title.pack(pady=5)
    
    if scram_key:
        scram_status = ctk.CTkLabel(scram_frame, text=f"Bound to: {scram_key}")
        scram_status.pack(pady=5)
        unbind_scram_btn = ctk.CTkButton(scram_frame, text="Remove Scram Bind", command=lambda: unbind_scram_settings())
        unbind_scram_btn.pack(pady=5)
    else:
        bind_scram_btn = ctk.CTkButton(scram_frame, text="Bind Scram Key", command=lambda: bind_scram_settings())
        bind_scram_btn.pack(pady=5)
    
    # Theme section
    theme_frame = ctk.CTkFrame(settings_window)
    theme_frame.pack(pady=10, padx=10, fill="x")
    theme_title = ctk.CTkLabel(theme_frame, text="Theme", font=ctk.CTkFont(size=16, weight="bold"))
    theme_title.pack(pady=5)
    
    theme_var = ctk.StringVar(value=theme)
    theme_menu = ctk.CTkOptionMenu(theme_frame, values=["System", "Light", "Dark"], variable=theme_var)
    theme_menu.pack(pady=5)
    
    # Replay section
    replay_frame = ctk.CTkFrame(settings_window)
    replay_frame.pack(pady=10, padx=10, fill="x")
    replay_title = ctk.CTkLabel(replay_frame, text="Macro Replay", font=ctk.CTkFont(size=16, weight="bold"))
    replay_title.pack(pady=5)
    
    replay_var = ctk.StringVar(value=replay_mode)
    once_radio = ctk.CTkRadioButton(replay_frame, text="Play once", variable=replay_var, value="once")
    once_radio.pack(pady=2)
    
    count_radio = ctk.CTkRadioButton(replay_frame, text="Play specified times", variable=replay_var, value="count")
    count_radio.pack(pady=2)
    
    count_entry = ctk.CTkEntry(replay_frame, placeholder_text="Number of times")
    count_entry.pack(pady=2)
    if replay_mode == "count":
        count_entry.insert(0, str(replay_count))
    
    infinite_radio = ctk.CTkRadioButton(replay_frame, text="Play infinitely until pressed again", variable=replay_var, value="infinite")
    infinite_radio.pack(pady=2)
    
    # Buttons
    button_frame = ctk.CTkFrame(settings_window, fg_color="transparent")
    button_frame.pack(pady=20)
    
    cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=close_settings_window)
    cancel_btn.pack(side="left", padx=10)
    
    reset_btn = ctk.CTkButton(button_frame, text="Reset to Defaults", fg_color="#ff9800", hover_color="#e68900", command=reset_to_defaults)
    reset_btn.pack(side="left", padx=10)
    
    save_btn = ctk.CTkButton(button_frame, text="Save", command=lambda: save_settings_popup(theme_var.get(), replay_var.get(), count_entry.get()))
    save_btn.pack(side="right", padx=10)

def reset_to_defaults():
    global theme, replay_mode, replay_count, scram_key, bindings
    theme = "System"
    replay_mode = "once"
    replay_count = 1
    scram_key = None
    bindings = {}
    save_settings()
    save_bindings()
    ctk.set_appearance_mode(theme)
    close_settings_window()

def unbind_scram():
    global scram_key
    if scram_key:
        print(f"Unbound scram from {scram_key}")
        scram_key = None
        save_bindings()

def bind_scram_settings():
    global recording, listener
    recording = True
    def on_press(key):
        global recording, scram_key
        if recording:
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            scram_key = k
            recording = False
            listener.stop()
            save_bindings()
            close_settings_window()
            open_settings()  # Refresh
    
    listener = keyboard.Listener(on_press=on_press)
    listener.start()

def unbind_scram_settings():
    global scram_key
    scram_key = None
    save_bindings()
    close_settings_window()
    open_settings()

def save_settings_popup(new_theme, new_replay, count_str):
    global theme, replay_mode, replay_count
    theme = new_theme
    replay_mode = new_replay
    if new_replay == "count":
        try:
            replay_count = int(count_str)
        except:
            replay_count = 1
    save_settings()
    ctk.set_appearance_mode(theme)
    close_settings_window()

# UI Elements
app = ctk.CTk()
app.geometry("1000x600")
app.title("MacroTS")

app.iconbitmap(resource_path("images/icon.ico"))

# Load settings icon
settings_icon = ctk.CTkImage(
    Image.open(resource_path("images/settings_icon.png")),
    size=(24, 24)
)

left_frame = ctk.CTkFrame(app, width=300)
right_frame = ctk.CTkFrame(app)

left_frame.pack(side="left", fill="y", padx=10, pady=10)
right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

operations_label = ctk.CTkLabel(right_frame, text="Macro Operations:", font=ctk.CTkFont(size=18, weight="bold"))
operations_label.pack(padx=10, pady=10)

operations_scrollable = ctk.CTkScrollableFrame(right_frame)
operations_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

bound_key_label = ctk.CTkLabel(left_frame, text="")
unbind_button = ctk.CTkButton(left_frame, text="Remove Bind", width=200, height=50, fg_color="#ff6b6b", hover_color="#ff5252", command=unbind_macro)

playing_label = ctk.CTkLabel(left_frame, text="Macro is playing...", font=ctk.CTkFont(size=16, weight="bold"), fg_color="#4CAF50", text_color="white")

title = ctk.CTkLabel(left_frame, text="MacroTS", font=ctk.CTkFont(size=32, weight="bold"))
title.pack(padx=10, pady=10)
settings_button = ctk.CTkButton(left_frame, image=settings_icon, text="", width=40, height=40, command=open_settings)
settings_button.pack(padx=10, pady=10)
load_macro_button = ctk.CTkButton(left_frame, text="Load Macro", width=200, height=50, fg_color="#1f6aa5", hover_color="#144a75", command=load_macro)
bind_macro_button = ctk.CTkButton(left_frame, text="Bind Macro", width=200, height=50, fg_color="#1f6aa5", hover_color="#144a75", command=bind_macro)
recording_label = ctk.CTkLabel(left_frame, text="Press a key to bind the macro")
cancel_button = ctk.CTkButton(left_frame, text="Cancel", width=200, height=50, fg_color="#ff0000", hover_color="#cc0000", command=stop_recording)
load_macro_button.pack(padx=10, pady=10)

load_bindings()
load_settings()
ctk.set_appearance_mode(theme)

display_operations()

global_listener = keyboard.Listener(on_press=on_global_press)
global_listener.start()

app.protocol("WM_DELETE_WINDOW", on_close)

app.mainloop()
