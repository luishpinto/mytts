import json
from pathlib import Path

def load_voice_map(path):
    return json.loads(Path(path).read_text(encoding="utf-8"))

def format_time(ms):
    h = ms // 3_600_000
    ms %= 3_600_000
    m = ms // 60_000
    ms %= 60_000
    s = ms // 1_000
    ms %= 1_000
    return f"{h:02d}:{m:02d}:{s:02d}.{ms:03d}"
