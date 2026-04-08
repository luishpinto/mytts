import re
import json

def split_inline_pauses(txt):
    parts = re.split(r'\{ *"pause" *: *(\d+) *\}', txt)
    segments = []

    for i in range(0, len(parts), 2):
        t = parts[i].strip()
        if not t:
            continue

        pause = int(parts[i + 1]) if i + 1 < len(parts) else 0
        segments.append((t, pause))

    return segments


def parse_script(text):
    slides = []
    current_slide = None
    pending_pause_before = 0

    current_comm = {"voice": "001", "rate": "+0%", "pitch": "+0Hz"}

    for line_number, raw_line in enumerate(text.splitlines(), start=1):
        line = raw_line.strip()
        if not line:
            continue

        if line.startswith("{") and line.endswith("}"):
            data = json.loads(line)

            if "slide" in data:
                current_slide = {"slide": data["slide"], "segments": []}
                slides.append(current_slide)

            elif "pause_before" in data:
                pending_pause_before = data["pause_before"]

            else:
                current_comm.update(data)

            continue

        if current_slide is None:
            raise ValueError(f"Text before slide-command at line {line_number}")

        segments = split_inline_pauses(line)

        for idx, (txt, pause) in enumerate(segments):
            seg = {
                "command": current_comm.copy(),
                "text": txt,
                "pause": pause,
                "pause_before": pending_pause_before if idx == 0 else 0,
            }

            pending_pause_before = 0
            current_slide["segments"].append(seg)

    return slides
