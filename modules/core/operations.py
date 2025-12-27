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
                if line.split(" ")[0] in ["press", "delay", "setting", "click", "type"]:
                    operations.append(line)
    except:
        pass
    return operations
