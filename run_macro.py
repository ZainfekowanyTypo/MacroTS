import pyautogui
from time import sleep
import sys

if len(sys.argv) > 1:
    file_path = sys.argv[1]
else:
    file_path = "example_macro.macrots"

loop_type = "once"
loop_count = 1

if len(sys.argv) > 2:
    loop_type = sys.argv[2]
if len(sys.argv) > 3 and loop_type == "count":
    try:
        loop_count = int(sys.argv[3])
    except:
        loop_count = 1

file = open(file_path)
operations = []
settings = []
available_operations = ["press", "delay", "setting", "click", "type"]

def readFileForOperations():
    for line in file:
        if line == '\n':
            continue

        operation = line.split(" ")[0]

        if operation in available_operations:
            if operation == "setting":
                settings.append(line.strip())
            else:
                operations.append(line.strip())

    return operations, settings

def defaultSettings(settings=None):
    if settings == "autogui_pause":
        return 0.1
    
    if settings is None:
        pyautogui.PAUSE = 0.1


def setSettings(sets):
    defaultSettings()

    for o in sets:
        o_name = o.split(" ")[0]
        o_content = o.split(" ")[1]

        if o_name != "setting":
            continue

        setting_name = o_content.split("=")[0]
        setting_value = o_content.split("=")[1]

        if setting_name == "autogui_pause":
            try:
                pause_time = float(setting_value)
                if pause_time < 0:
                    pyautogui.PAUSE = defaultSettings("autogui_pause")
                else:
                    pyautogui.PAUSE = pause_time
            except ValueError:
                continue

def executeOps(ops):
    if not ops:
        return

    for o in ops:
        parts = o.split(" ", 1)
        o_name = parts[0]
        o_content = parts[1] if len(parts) > 1 else ""
        
        if o_name == "type" and o_content.startswith("type "):
            o_content = o_content[5:]

        if o_name not in available_operations:
            continue

        # execute operation
        if o_name == "press":
            if not pyautogui.isValidKey(o_content):
                continue

            pyautogui.press(o_content)

        elif o_name == "delay":
            try:
                delay_time = float(o_content)
                if delay_time < 0:
                    continue
                sleep(delay_time)
            except ValueError:
                continue

        elif o_name == "click":
            if '(' in o_content:
                mousebutton = o_content.split('(')[0]
                try:
                    pos_str = o_content.split('(')[1].replace(')', '')
                    pos = pos_str.split(',')
                    if len(pos) != 2:
                        continue
                    x = int(pos[0]) if pos[0].strip() else None
                    y = int(pos[1]) if pos[1].strip() else None
                except (IndexError, ValueError):
                    continue
            else:
                mousebutton = o_content
                x = y = None

            if mousebutton == "left":
                if x is None and y is None:
                    pyautogui.click()
                else:
                    pyautogui.click(x, y)
            elif mousebutton == "right":
                if x is None and y is None:
                    pyautogui.rightClick()
                else:
                    pyautogui.rightClick(x, y)
            elif mousebutton == "middle":
                if x is None and y is None:
                    pyautogui.middleClick()
                else:
                    pyautogui.middleClick(x, y)
            elif mousebutton == "double_left":
                if x is None and y is None:
                    pyautogui.doubleClick()
                else:
                    pyautogui.doubleClick(x, y)
            else:
                continue
        elif o_name == "type":
            pyautogui.typewrite(o_content, interval=pyautogui.PAUSE)

ops, sets = readFileForOperations()

setSettings(sets)

if loop_type == "once":
    executeOps(ops)
elif loop_type == "count":
    for _ in range(loop_count):
        executeOps(ops)
elif loop_type == "infinite":
    while True:
        executeOps(ops)

