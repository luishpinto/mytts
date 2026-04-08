import asyncio
import uuid

import edge_tts
from pydub import AudioSegment
from pydub.effects import low_pass_filter, high_pass_filter, normalize

from core.utils import format_time


def enhance_voice(audio):
    audio = high_pass_filter(audio, cutoff=80)
    audio = low_pass_filter(audio, cutoff=9000)
    return normalize(audio)


def silence(ms):
    return AudioSegment.silent(duration=ms)


def build_audio(dirs, slides, voice_map, subtitles_enabled=False):
    full_audio = AudioSegment.empty()
    seg_count = 1
    tran_ms = 500

    for slide in slides:
        slide_path = dirs["audio"] / f'{slide["slide"]:04d}.mp3'

        subtitles = None
        if subtitles_enabled:
            srt_path = dirs["audio"] / f'{slide["slide"]:04d}.srt'
            subtitles = open(srt_path, "w", encoding="utf-8")

        time_ms = 0
        slide_audio = AudioSegment.empty()

        for segment in slide["segments"]:
            tmp_path = dirs["temp"] / f"{uuid.uuid4()}.mp3"
            comm = segment["command"]

            async def get_speech():
                tts = edge_tts.Communicate(
                    segment["text"],
                    voice=voice_map.get(comm["voice"]),
                    rate=comm["rate"],
                    pitch=comm["pitch"],
                )
                await tts.save(str(tmp_path))

            asyncio.run(get_speech())

            seg_audio = AudioSegment.empty()
            seg_audio += silence(segment["pause_before"] * 1000)

            start_ms = time_ms + len(seg_audio)

            tmp_audio = enhance_voice(AudioSegment.from_mp3(tmp_path))
            seg_audio += tmp_audio

            end_ms = start_ms + len(tmp_audio)
            seg_audio += silence(segment["pause"] * 1000)

            if subtitles_enabled:
                subtitles.write(
                    f"{seg_count}\n"
                    f"{format_time(start_ms + tran_ms)} --> {format_time(end_ms + tran_ms)}\n"
                    f"{segment['text']}\n\n"
                )

            time_ms += len(seg_audio)
            seg_count += 1
            slide_audio += seg_audio

            tmp_path.unlink()

        full_audio += slide_audio
        slide_audio.export(slide_path, format="mp3")

        if subtitles:
            subtitles.close()

    full_audio.export(dirs["full_audio"], format="mp3")
