import os
import uuid
import asyncio
from typing import List, Dict

import edge_tts
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter, normalize


def enhance_voice(audio: AudioSegment) -> AudioSegment:
    """
    Improve voice quality
    """
    audio = high_pass_filter(audio, cutoff=80)
    audio = low_pass_filter(audio, cutoff=9000)
    audio = normalize(audio)
    return audio


def silence(ms: int) -> AudioSegment:
    return AudioSegment.silent(duration=ms)


async def _generate_tts(text: str, voice: str, rate: str, pitch: str, output_path: str):
    communicate = edge_tts.Communicate(
        text,
        voice=voice,
        rate=rate,
        pitch=pitch
    )
    await communicate.save(output_path)


def build_audio(
    slides: List[Dict],
    voice_map: Dict[str, str],
    audio_dir: str,
    subtitles_enabled: bool = False
):
    full_audio = AudioSegment.empty()
    tran_ms = 500
    seg_count = 1

    for slide in slides:
        slide_audio = AudioSegment.empty()
        time_ms = 0

        mp3_slide_path = os.path.join(audio_dir, f'{slide["slide"]:04d}.mp3')

        subtitles = None
        if subtitles_enabled:
            subtitles_path = os.path.join(audio_dir, f'{slide["slide"]:04d}.srt')
            subtitles = open(subtitles_path, "w", encoding="utf-8")

        for segment in slide["segments"]:
            mp3_seg_path = os.path.join(audio_dir, f"tmp_{uuid.uuid4()}.mp3")

            comm = segment["command"]

            asyncio.run(
                _generate_tts(
                    segment["text"],
                    voice_map.get(comm["voice"]),
                    comm["rate"],
                    comm["pitch"],
                    mp3_seg_path
                )
            )

            seg_audio = AudioSegment.empty()

            seg_audio += silence(segment["pause_before"] * 1000)

            start_ms = time_ms + len(seg_audio)

            tmp_audio = AudioSegment.from_mp3(mp3_seg_path)
            tmp_audio = enhance_voice(tmp_audio)

            seg_audio += tmp_audio

            end_ms = start_ms + len(tmp_audio)

            seg_audio += silence(segment["pause"] * 1000)

            if subtitles_enabled:
                from .utils import format_time

                subtitles.write(
                    f"{seg_count}\n"
                    f"{format_time(start_ms + tran_ms)} --> {format_time(end_ms + tran_ms)}\n"
                    f"{segment['text']}\n\n"
                )

            time_ms += len(seg_audio)
            seg_count += 1

            slide_audio += seg_audio
            os.remove(mp3_seg_path)

        slide_audio.export(mp3_slide_path, format="mp3")
        full_audio += slide_audio

        if subtitles_enabled:
            subtitles.close()

    full_audio.export("./full_audio.mp3", format="mp3")
