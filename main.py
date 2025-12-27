from modules.ui.main_window import MainWindow
from modules.core import bindings as b
from modules.core import settings as s


# ------------------ Load Initial Data ------------------
b.load_bindings()   # Load macro bindings & scram key
s.load_settings()   # Load theme, replay mode, count

# ------------------ Apply Theme ------------------
import customtkinter as ctk
ctk.set_appearance_mode(s.theme)
ctk.set_default_color_theme("blue")

# ------------------ Start Main Window ------------------
if __name__ == "__main__":
    # Instantiate and run the UI
    app = MainWindow()
    app.run()
