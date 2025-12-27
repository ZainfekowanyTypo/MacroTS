from modules.ui.main_window import MainWindow
from modules.core import bindings as b
from modules.core import settings as s

import customtkinter as ctk

b.load_bindings() 
s.load_settings()

ctk.set_appearance_mode(s.theme)
ctk.set_default_color_theme("blue")

if __name__ == "__main__":
    # Instantiate and run the UI
    app = MainWindow()
    app.run()
