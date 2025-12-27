import os
import sys
import threading
import tkinter as tk
import customtkinter as ctk
from PIL import Image
from tkinter import filedialog
from pynput import keyboard

from modules.core import bindings as b
from modules.core import settings as s
from modules.core import operations as op
from modules.core.global_listener import start_global_listener
from modules.ui import settings_window
from modules.core.utils import resource_path

class MainWindow:
    def __init__(self):
        self.file_path = None
        self.recording = False
        self.listener = None

        # Main window
        self.app = ctk.CTk()
        self.app.geometry("1000x600")
        self.app.title("MacroTS")
        self.app.iconbitmap(resource_path("images/icon.ico"))

        # Load settings icon
        self.settings_icon = ctk.CTkImage(
            Image.open(resource_path("images/settings_icon.png")),
            size=(24, 24)
        )

        # Frames
        self.left_frame = ctk.CTkFrame(self.app, width=300)
        self.right_frame = ctk.CTkFrame(self.app)
        self.left_frame.pack(side="left", fill="y", padx=10, pady=10)
        self.right_frame.pack(side="right", fill="both", expand=True, padx=10, pady=10)

        # Right Frame - Operations
        self.operations_label = ctk.CTkLabel(self.right_frame, text="Macro Operations:", font=ctk.CTkFont(size=18, weight="bold"))
        self.operations_label.pack(padx=10, pady=10)
        self.operations_scrollable = ctk.CTkScrollableFrame(self.right_frame)
        self.operations_scrollable.pack(fill="both", expand=True, padx=10, pady=10)

        # Left Frame - Main UI
        self.title_label = ctk.CTkLabel(self.left_frame, text="MacroTS", font=ctk.CTkFont(size=32, weight="bold"))
        self.title_label.pack(padx=10, pady=10)

        self.settings_button = ctk.CTkButton(self.left_frame, image=self.settings_icon, text="", width=40, height=40,
                                             command=self.open_settings)
        self.settings_button.pack(padx=10, pady=10)

        self.load_macro_button = ctk.CTkButton(self.left_frame, text="Load Macro", width=200, height=50,
                                               fg_color="#1f6aa5", hover_color="#144a75", command=self.load_macro)
        self.bind_macro_button = ctk.CTkButton(self.left_frame, text="Bind Macro", width=200, height=50,
                                               fg_color="#1f6aa5", hover_color="#144a75", command=self.bind_macro)
        self.recording_label = ctk.CTkLabel(self.left_frame, text="Press a key to bind the macro")
        self.cancel_button = ctk.CTkButton(self.left_frame, text="Cancel", width=200, height=50,
                                           fg_color="#ff0000", hover_color="#cc0000", command=self.stop_recording)
        self.bound_key_label = ctk.CTkLabel(self.left_frame, text="")
        self.unbind_button = ctk.CTkButton(self.left_frame, text="Remove Bind", width=200, height=50,
                                           fg_color="#ff6b6b", hover_color="#ff5252", command=self.unbind_macro)
        self.playing_label = ctk.CTkLabel(self.left_frame, text="Macro is playing...", font=ctk.CTkFont(size=16, weight="bold"),
                                          fg_color="#4CAF50", text_color="white")

        self.load_macro_button.pack(padx=10, pady=10)

        # Load saved bindings and settings
        b.load_bindings()
        s.load_settings()
        ctk.set_appearance_mode(s.theme)

        # Display operations if macro loaded
        self.display_operations()

        # Start global listener (pass hide_playing_label)
        self.global_listener = start_global_listener(
            self.enable_macro_buttons,
            self.disable_macro_buttons,
            self.show_playing_label,
            self.hide_playing_label
        )

        self.app.protocol("WM_DELETE_WINDOW", self.on_close)

    # ---------------------------- Utility Methods ----------------------------

    def display_operations(self):
        # Clear previous
        for widget in self.operations_scrollable.winfo_children():
            widget.destroy()

        if not self.file_path:
            no_macro_label = ctk.CTkLabel(self.operations_scrollable, text="No macro loaded")
            no_macro_label.pack(padx=10, pady=5)
            return

        operations = op.read_macro_operations(self.file_path)
        if not operations:
            no_ops_label = ctk.CTkLabel(self.operations_scrollable, text="No operations found")
            no_ops_label.pack(padx=10, pady=5)
            return

        for i, operation in enumerate(operations, 1):
            op_label = ctk.CTkLabel(self.operations_scrollable, text=f"{i}. {operation}", anchor="w")
            op_label.pack(fill="x", padx=10, pady=2)

    def load_macro(self):
        self.file_path = filedialog.askopenfilename(
            title="Select MacroTS File",
            filetypes=[("MacroTS files", "*.macrots"), ("All files", "*")]
        )
        if self.file_path:
            print(f"Selected file: {self.file_path}")
            self.bind_macro_button.pack(after=self.load_macro_button, padx=10, pady=10)
        else:
            self.bind_macro_button.pack_forget()

        self.update_bound_label()
        self.display_operations()
        return self.file_path

    def bind_macro(self):
        if not self.file_path:
            print("No macro file selected.")
            return

        # Hide bound labels during recording
        self.bound_key_label.pack_forget()
        self.unbind_button.pack_forget()

        self.recording = True
        self.recording_label.pack(after=self.bind_macro_button, padx=10, pady=10)
        self.load_macro_button.configure(state="disabled")
        self.bind_macro_button.configure(state="disabled")
        self.cancel_button.pack(after=self.recording_label, padx=10, pady=10)

        def on_press(key):
            if not self.recording:
                return
            try:
                k = key.char
            except AttributeError:
                k = str(key)
            b.bind_macro(k, self.file_path)
            print(f"Bound {k} to {self.file_path}")
            self.stop_recording()
            self.update_bound_label()

        self.listener = keyboard.Listener(on_press=on_press)
        self.listener.start()

    def stop_recording(self):
        self.recording = False
        self.recording_label.pack_forget()
        self.cancel_button.pack_forget()
        self.load_macro_button.configure(state="normal")
        self.bind_macro_button.configure(state="normal")
        if hasattr(self, "listener") and self.listener:
            self.listener.stop()
            self.listener = None
        self.update_bound_label()

    def update_bound_label(self):
        if self.file_path:
            reverse = {v: k for k, v in b.bindings.items()}
            if self.file_path in reverse:
                key = reverse[self.file_path]
                self.bound_key_label.configure(text=f"Bound to: {key}")
                self.bound_key_label.pack(after=self.bind_macro_button, padx=10, pady=10)
                self.unbind_button.pack(after=self.bound_key_label, padx=10, pady=10)
            else:
                self.bound_key_label.configure(text="")
                self.bound_key_label.pack_forget()
                self.unbind_button.pack_forget()
        else:
            self.bound_key_label.configure(text="")
            self.bound_key_label.pack_forget()
            self.unbind_button.pack_forget()

    def unbind_macro(self):
        if self.file_path:
            b.unbind_macro(self.file_path)
            print(f"Unbound {self.file_path}")
            self.update_bound_label()

    # ---------------------------- UI Methods ----------------------------

    def open_settings(self):
        settings_window.open_settings(self.app)

    def disable_macro_buttons(self):
        self.load_macro_button.configure(state="disabled")
        self.bind_macro_button.configure(state="disabled")
        self.unbind_button.configure(state="disabled")

    def enable_macro_buttons(self):
        self.load_macro_button.configure(state="normal")
        self.bind_macro_button.configure(state="normal")
        self.unbind_button.configure(state="normal")
        self.update_bound_label()

    def show_playing_label(self):
        self.playing_label.pack(after=self.title_label, padx=10, pady=5)

    def hide_playing_label(self):
        self.playing_label.pack_forget()

    def on_close(self):
        if self.global_listener:
            self.global_listener.stop()
        self.app.destroy()

    def run(self):
        self.app.mainloop()


if __name__ == "__main__":
    MainWindow().run()
