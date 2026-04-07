import argparse
import os

from mytts import (
    parse_script,
    build_audio,
    pdf_to_png,
    create_all_slide_videos,
    concat_videos,
    load_voice_map
)
from mytts.utils import clean_output_dir

def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_txt")
    parser.add_argument("--pdf")
    parser.add_argument("-v", "--voices", default="voices.json")
    parser.add_argument("--subtitles", action="store_true")

    args = parser.parse_args()

    audio_dir = "./.audio_out"
    video_dir = "./.video_out"

    os.makedirs(audio_dir, exist_ok=True)
    os.makedirs(video_dir, exist_ok=True)

    clean_output_dir(audio_dir)
    clean_output_dir(video_dir)

    text = open(args.input_txt, encoding="utf-8").read()
    slides = parse_script(text)

    voice_map = load_voice_map(args.voices)

    build_audio(slides, voice_map, audio_dir, subtitles_enabled=args.subtitles)

    if args.pdf:
        pdf_to_png(args.pdf, video_dir)
        videos = create_all_slide_videos(audio_dir, video_dir, args.subtitles)
        concat_videos(videos)

if __name__ == "__main__":
    main()
