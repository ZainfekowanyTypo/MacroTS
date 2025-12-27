import customtkinter as ctk
from pynput import keyboard
from modules.core import settings as s
from modules.core import bindings as b

settings_window = None
_parent_window = None  # store the parent

def open_settings(parent):
    global settings_window, _parent_window
    _parent_window = parent  # store the parent reference
    if settings_window and settings_window.winfo_exists():
        settings_window.focus()
        return

    settings_window = ctk.CTkToplevel(parent)
    settings_window.title("Settings")
    settings_window.geometry("400x500")
    settings_window.resizable(False, False)
    settings_window.protocol("WM_DELETE_WINDOW", lambda: close_settings_window())
    settings_window.transient(parent)
    settings_window.grab_set()

    # ------------------ Scram Key Section ------------------
    scram_frame = ctk.CTkFrame(settings_window)
    scram_frame.pack(pady=10, padx=10, fill="x")
    scram_title = ctk.CTkLabel(scram_frame, text="Scram Key", font=ctk.CTkFont(size=16, weight="bold"))
    scram_title.pack(pady=5)

    def bind_scram():
        def on_press(key):
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            b.bind_scram(k)
            listener.stop()
            if _parent_window:  # make sure parent exists
                _parent_window.after(0, refresh_settings)
                
        listener = keyboard.Listener(on_press=on_press)
        listener.start()

    def unbind_scram():
        b.unbind_scram()
        refresh_settings()

    # show correct buttons
    for widget in scram_frame.winfo_children()[1:]:
        widget.destroy()

    if b.scram_key:
        scram_status = ctk.CTkLabel(scram_frame, text=f"Bound to: {b.scram_key}")
        scram_status.pack(pady=5)
        unbind_btn = ctk.CTkButton(scram_frame, text="Remove Scram Bind", command=unbind_scram)
        unbind_btn.pack(pady=5)
    else:
        bind_btn = ctk.CTkButton(scram_frame, text="Bind Scram Key", command=bind_scram)
        bind_btn.pack(pady=5)

    # ------------------ Theme Section ------------------
    theme_frame = ctk.CTkFrame(settings_window)
    theme_frame.pack(pady=10, padx=10, fill="x")
    theme_title = ctk.CTkLabel(theme_frame, text="Theme", font=ctk.CTkFont(size=16, weight="bold"))
    theme_title.pack(pady=5)

    theme_var = ctk.StringVar(value=s.theme)
    theme_menu = ctk.CTkOptionMenu(theme_frame, values=["System", "Light", "Dark"], variable=theme_var)
    theme_menu.pack(pady=5)

    # ------------------ Replay Section ------------------
    replay_frame = ctk.CTkFrame(settings_window)
    replay_frame.pack(pady=10, padx=10, fill="x")
    replay_title = ctk.CTkLabel(replay_frame, text="Macro Replay", font=ctk.CTkFont(size=16, weight="bold"))
    replay_title.pack(pady=5)

    replay_var = ctk.StringVar(value=s.replay_mode)
    once_radio = ctk.CTkRadioButton(replay_frame, text="Play once", variable=replay_var, value="once")
    once_radio.pack(pady=2)
    count_radio = ctk.CTkRadioButton(replay_frame, text="Play specified times", variable=replay_var, value="count")
    count_radio.pack(pady=2)
    count_entry = ctk.CTkEntry(replay_frame, placeholder_text="Number of times")
    count_entry.pack(pady=2)
    if s.replay_mode == "count":
        count_entry.insert(0, str(s.replay_count))
    infinite_radio = ctk.CTkRadioButton(replay_frame, text="Play infinitely until pressed again", variable=replay_var, value="infinite")
    infinite_radio.pack(pady=2)

    # ------------------ Buttons ------------------
    button_frame = ctk.CTkFrame(settings_window, fg_color="transparent")
    button_frame.pack(pady=20)
    cancel_btn = ctk.CTkButton(button_frame, text="Cancel", command=close_settings_window)
    cancel_btn.pack(side="left", padx=10)
    reset_btn = ctk.CTkButton(button_frame, text="Reset to Defaults", fg_color="#ff9800", hover_color="#e68900",
                              command=reset_to_defaults)
    reset_btn.pack(side="left", padx=10)
    save_btn = ctk.CTkButton(button_frame, text="Save", command=lambda: save_settings(theme_var.get(), replay_var.get(), count_entry.get()))
    save_btn.pack(side="right", padx=10)

def close_settings_window():
    global settings_window
    if settings_window:
        settings_window.grab_release()
        settings_window.destroy()
        settings_window = None

def refresh_settings():
    global _parent_window
    close_settings_window()
    if _parent_window:  # only reopen if parent exists
        open_settings(_parent_window)

def reset_to_defaults():
    s.reset_settings()
    b.bindings.clear()
    b.scram_key = None
    b.save_bindings()
    refresh_settings()

def save_settings(new_theme, new_replay, count_str):
    s.theme = new_theme
    s.replay_mode = new_replay
    if new_replay == "count":
        try:
            s.replay_count = int(count_str)
        except:
            s.replay_count = 1
    s.save_settings()
    close_settings_window()
