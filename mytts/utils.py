import os
import json
import shutil

def load_voice_map(path):
    with open(path, "r", encoding="utf-8") as f:
        return json.load(f)

def clean_output_dir(path):
    if not os.path.exists(path):
        return

    for name in os.listdir(path):
        full_path = os.path.join(path, name)

        if os.path.isfile(full_path) or os.path.islink(full_path):
            os.remove(full_path)
        elif os.path.isdir(full_path):
            shutil.rmtree(full_path)

def format_time(ms):
    hours = ms // 3_600_000
    ms %= 3_600_000
    minutes = ms // 60_000
    ms %= 60_000
    seconds = ms // 1_000
    milliseconds = ms % 1_000

    return f"{hours:02d}:{minutes:02d}:{seconds:02d}.{milliseconds:03d}"
