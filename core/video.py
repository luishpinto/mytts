import subprocess
from pathlib import Path
from pdf2image import convert_from_path


def pdf_to_png(dirs, pdf_path):
    images = convert_from_path(pdf_path, dpi=300)

    for i, img in enumerate(images):
        img.save(dirs["video"] / f"slide_{i+1:04d}.png")


def create_slide_video(dirs, image_path, audio_path, video_path, subtitles_enabled):
    vf = "scale=1280:720:force_original_aspect_ratio=decrease,pad=1280:720:(ow-iw)/2:(oh-ih)/2"

    if subtitles_enabled:
        idx = audio_path.stem
        srt = dirs["audio"] / f"{idx}.srt"
        fonts = Path("assets/fonts").resolve()

        vf = (
            f"subtitles='{srt}':fontsdir={fonts}:force_style='Fontname=Roboto Condensed,"
            "Fontsize=12,PrimaryColour=&H000000,Outline=0,MarginV=25',"
            + vf
        )

    cmd = [
        "ffmpeg", "-y",
        "-loop", "1", "-i", str(image_path),
        "-i", str(audio_path),
        "-c:v", "libx264",
        "-tune", "stillimage",
        "-c:a", "aac",
        "-pix_fmt", "yuv420p",
        "-shortest",
        "-vf", vf,
        str(video_path)
    ]

    subprocess.run(cmd, check=True)


def create_all_slide_videos(dirs, subtitles_enabled):
    videos = []

    for audio_file in sorted(dirs["audio"].glob("*.mp3")):
        idx = audio_file.stem
        image = dirs["video"] / f"slide_{idx}.png"
        video = dirs["video"] / f"slide_{idx}.mp4"

        create_slide_video(dirs, image, audio_file, video, subtitles_enabled)
        videos.append(video)

    return videos


def concat_videos(dirs, videos):
    list_file = dirs["temp"] / "concat.txt"

    with open(list_file, "w") as f:
        for v in videos:
            f.write(f"file '{v.resolve()}'\n")

    subprocess.run([
        "ffmpeg", "-y",
        "-f", "concat",
        "-safe", "0",
        "-i", str(list_file),
        "-c", "copy",
        "-movflags", "+faststart",
        str(dirs["final_video"])
    ], check=True)
