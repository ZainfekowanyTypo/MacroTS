import pyautogui
from time import sleep

available_operations = ["press", "delay", "setting", "click", "type"]

def execute_macro(file_path, loop_type="once", loop_count=1, stop_event=None):
    operations = []
    settings = []

    with open(file_path, "r") as f:
        for line in f:
            if not line.strip():
                continue
            op_name = line.split(" ")[0]
            if op_name in available_operations:
                if op_name == "setting":
                    settings.append(line.strip())
                else:
                    operations.append(line.strip())

    # Apply settings
    pyautogui.PAUSE = 0.1
    for o in settings:
        _, content = o.split(" ", 1)
        setting_name, setting_value = content.split("=")
        if setting_name == "autogui_pause":
            try:
                pyautogui.PAUSE = max(float(setting_value), 0.1)
            except ValueError:
                pass

    def execute_ops(ops):
        for o in ops:
            if stop_event and stop_event.is_set():
                return
            parts = o.split(" ", 1)
            o_name = parts[0]
            o_content = parts[1] if len(parts) > 1 else ""
            if o_name == "type" and o_content.startswith("type "):
                o_content = o_content[5:]
            if o_name not in available_operations:
                continue

            if o_name == "press":
                if stop_event and stop_event.is_set():
                    return
                if pyautogui.isValidKey(o_content):
                    pyautogui.press(o_content)

            elif o_name == "delay":
                try:
                    t = float(o_content)
                    elapsed = 0
                    interval = 0.05
                    while elapsed < t:
                        if stop_event and stop_event.is_set():
                            return
                        sleep(interval)
                        elapsed += interval
                except ValueError:
                    continue

            elif o_name == "click":
                if stop_event and stop_event.is_set():
                    return
                if "(" in o_content:
                    button = o_content.split("(")[0]
                    pos_str = o_content.split("(")[1].replace(")", "")
                    x = y = None
                    try:
                        coords = pos_str.split(",")
                        if len(coords) == 2:
                            x = int(coords[0].strip()) if coords[0].strip() else None
                            y = int(coords[1].strip()) if coords[1].strip() else None
                    except:
                        pass
                else:
                    button = o_content
                    x = y = None

                if button == "left":
                    pyautogui.click(x, y)
                elif button == "right":
                    pyautogui.rightClick(x, y)
                elif button == "middle":
                    pyautogui.middleClick(x, y)
                elif button == "double_left":
                    pyautogui.doubleClick(x, y)

            elif o_name == "type":
                for char in o_content:
                    if stop_event and stop_event.is_set():
                        return
                    pyautogui.typewrite(char, interval=pyautogui.PAUSE)

    # Loop execution
    if loop_type == "once":
        execute_ops(operations)
    elif loop_type == "count":
        for _ in range(loop_count):
            if stop_event and stop_event.is_set():
                break
            execute_ops(operations)
    elif loop_type == "infinite":
        while not (stop_event and stop_event.is_set()):
            execute_ops(operations)
