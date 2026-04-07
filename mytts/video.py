import os
import re
import subprocess
from typing import List


def create_slide_video(
    image_path: str,
    audio_path: str,
    video_path: str,
    subtitles_enabled: bool,
    audio_dir: str
):
    if not os.path.exists(image_path):
        raise FileNotFoundError(image_path)

    if not os.path.exists(audio_path):
        raise FileNotFoundError(audio_path)

    idx = os.path.splitext(os.path.basename(audio_path))[0]

    vf_filter = (
        "scale=1280:720:force_original_aspect_ratio=decrease,"
        "pad=1280:720:(ow-iw)/2:(oh-ih)/2"
    )

    if subtitles_enabled:
        subtitle_path = os.path.join(audio_dir, f"{idx}.srt")

        if not os.path.exists(subtitle_path):
            raise FileNotFoundError(subtitle_path)

        subtitle_path = subtitle_path.replace("\\", "/")

        vf_filter = (
            f"subtitles='{subtitle_path}':fontsdir=./.ttf_fonts:"
            "force_style='Fontname=Roboto Condensed,Fontsize=12,"
            "PrimaryColour=&H000000,Outline=0,MarginV=25',"
            + vf_filter
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", image_path,
        "-i", audio_path,
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", vf_filter,
        video_path
    ]

    subprocess.run(cmd, check=True)


def create_all_slide_videos(audio_dir: str, video_dir: str, subtitles_enabled: bool) -> List[str]:
    videos = []

    mp3_files = sorted(
        f for f in os.listdir(audio_dir)
        if re.match(r"^\d{4}\.mp3$", f)
    )

    for f in mp3_files:
        idx = os.path.splitext(f)[0]

        audio_path = os.path.join(audio_dir, f)
        image_path = os.path.join(video_dir, f"slide_{idx}.png")
        video_path = os.path.join(video_dir, f"slide_{idx}.mp4")

        create_slide_video(image_path, audio_path, video_path, subtitles_enabled, audio_dir)
        videos.append(video_path)

    return videos


def concat_videos(videos: List[str], output_path: str = "./final_video.mp4"):
    list_file = "concat.txt"

    with open(list_file, "w") as f:
        for v in videos:
            f.write(f"file '{os.path.abspath(v)}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", list_file,
        "-c", "copy",
        "-movflags", "+faststart",
        output_path
    ], check=True)

    os.remove(list_file)
