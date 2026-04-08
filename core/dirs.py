from pathlib import Path
from datetime import datetime

def create_run_dirs(base="runs"):
    ts = datetime.now().strftime("%Y%m%d_%H%M%S")
    root = Path(base) / f"run_{ts}"

    dirs = {
        "root": root,
        "audio": root / "audio",
        "video": root / "video",
        "temp": root / "temp",
        "full_audio": root / "full_audio.mp3",
        "final_video": root / "final_video.mp4",
    }

    for d in ["audio", "video", "temp"]:
        dirs[d].mkdir(parents=True, exist_ok=True)

    return dirs
