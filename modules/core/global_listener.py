import threading
from modules.core import bindings as b
from modules.core import settings as s
from modules.macros import run_macro

current_macro_thread = None
stop_event = threading.Event()

def macro_thread_runner(file_path, loop_type, loop_count, on_finish_callback):
    stop_event.clear()

    def patched_sleep(seconds):
        import time
        elapsed = 0
        interval = 0.05
        while elapsed < seconds:
            if stop_event.is_set():
                raise KeyboardInterrupt
            time.sleep(interval)
            elapsed += interval

    import builtins
    original_sleep = builtins.sleep if hasattr(builtins, "sleep") else None
    import time
    builtins.sleep = patched_sleep

    try:
        run_macro.execute_macro(file_path, loop_type, loop_count)
    except KeyboardInterrupt:
        pass
    finally:
        if original_sleep:
            builtins.sleep = original_sleep
        on_finish_callback()

def on_global_press(key, enable_buttons_callback, disable_buttons_callback, show_playing_label_callback, hide_playing_label_callback):
    global current_macro_thread, stop_event

    try:
        k = key.char
    except AttributeError:
        k = str(key)

    # Stop macro (scram key)
    if k == b.scram_key:
        if current_macro_thread and current_macro_thread.is_alive():
            stop_event.set()
            current_macro_thread = None
            enable_buttons_callback()
            hide_playing_label_callback()

    # Start macro
    elif k in b.bindings:
        macro_path = b.bindings[k]
        loop_type = s.replay_mode
        loop_count = s.replay_count if loop_type == "count" else 1

        # If macro already running, stop it
        if current_macro_thread and current_macro_thread.is_alive():
            stop_event.set()
            current_macro_thread = None
            enable_buttons_callback()
            hide_playing_label_callback()
        else:
            disable_buttons_callback()
            show_playing_label_callback()
            stop_event.clear()
            current_macro_thread = threading.Thread(
                target=lambda: [run_macro.execute_macro(macro_path, loop_type, loop_count, stop_event),
                                enable_buttons_callback(),
                                hide_playing_label_callback()],
                daemon=True
            )
            current_macro_thread.start()

def start_global_listener(enable_buttons_callback, disable_buttons_callback, show_playing_label_callback, hide_playing_label_callback):
    from pynput import keyboard
    listener = keyboard.Listener(
        on_press=lambda key: on_global_press(
            key,
            enable_buttons_callback,
            disable_buttons_callback,
            show_playing_label_callback,
            hide_playing_label_callback
        )
    )
    listener.start()
    return listener
