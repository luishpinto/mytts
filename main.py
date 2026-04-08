#! /usr/bin/env python3
# -*- coding: utf-8 -*-

import argparse
from pathlib import Path

from core.dirs import create_run_dirs
from core.parser import parse_script
from core.audio import build_audio
from core.video import pdf_to_png, create_all_slide_videos, concat_videos
from core.utils import load_voice_map


def main():
    parser = argparse.ArgumentParser()

    parser.add_argument("input_txt")
    parser.add_argument("--pdf")
    parser.add_argument("-v", "--voices", default="voices.json")
    parser.add_argument("--subtitles", action="store_true")
    parser.add_argument("--out", default="runs")

    args = parser.parse_args()

    dirs = create_run_dirs(args.out)

    text = Path(args.input_txt).read_text(encoding="utf-8")
    slides = parse_script(text)

    voice_map = load_voice_map(args.voices)

    build_audio(dirs, slides, voice_map, args.subtitles)

    if args.pdf:
        pdf_to_png(dirs, args.pdf)
        videos = create_all_slide_videos(dirs, args.subtitles)
        concat_videos(dirs, videos)


if __name__ == "__main__":
    main()
