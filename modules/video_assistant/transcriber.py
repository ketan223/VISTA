"""
VISTA AI Video Assistant - Transcription Engine
Uses Faster-Whisper to provide high-speed, local speech-to-text with segment timestamps.
Also supports optional cloud Indic translation via Sarvam AI when configured.
"""

import os
import requests
from typing import List, Dict, Any, Optional
from faster_whisper import WhisperModel
from pydub import AudioSegment

from config import (
    WHISPER_MODEL,
    WHISPER_DEVICE,
    WHISPER_COMPUTE_TYPE,
    SARVAM_API_KEY,
    SARVAM_STT_MODEL,
)

_cached_model: Optional[WhisperModel] = None
_cached_model_size: Optional[str] = None

def format_timestamp(seconds: float) -> str:
    """Format seconds into HH:MM:SS or MM:SS."""
    seconds = max(0.0, float(seconds))
    hrs = int(seconds // 3600)
    mins = int((seconds % 3600) // 60)
    secs = int(seconds % 60)
    if hrs > 0:
        return f"{hrs:02d}:{mins:02d}:{secs:02d}"
    return f"{mins:02d}:{secs:02d}"

def get_whisper_model(model_size: str = WHISPER_MODEL) -> WhisperModel:
    global _cached_model, _cached_model_size
    if _cached_model is None or _cached_model_size != model_size:
        print(f"[Transcriber] Loading Faster-Whisper model '{model_size}' on {WHISPER_DEVICE} ({WHISPER_COMPUTE_TYPE})...")
        _cached_model = WhisperModel(
            model_size,
            device=WHISPER_DEVICE,
            compute_type=WHISPER_COMPUTE_TYPE,
        )
        _cached_model_size = model_size
        print(f"[Transcriber] Model '{model_size}' loaded successfully.")
    return _cached_model

LANGUAGE_MAP = {
    "english": "en",
    "en": "en",
    "hindi": "hi",
    "hi": "hi",
    "spanish": "es",
    "es": "es",
    "french": "fr",
    "fr": "fr",
    "german": "de",
    "de": "de",
    "auto": None,
    "hinglish": None,
}

def transcribe_with_whisper(
    wav_path: str,
    language: Optional[str] = None,
    model_size: str = WHISPER_MODEL,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Transcribe audio with Faster-Whisper, preserving segment timestamps.
    """
    model = get_whisper_model(model_size)
    lang_param = LANGUAGE_MAP.get(language.lower(), None) if language else None

    if progress_callback:
        progress_callback(10, f"Initializing transcription with Faster-Whisper ({model_size})...")

    segments_generator, info = model.transcribe(
        wav_path,
        language=lang_param,
        beam_size=5,
        vad_filter=True,
        vad_parameters=dict(min_silence_duration_ms=500),
    )

    detected_lang = info.language
    duration = info.duration or 1.0

    segments = []
    formatted_lines = []
    plain_texts = []

    for i, seg in enumerate(segments_generator):
        start_str = format_timestamp(seg.start)
        end_str = format_timestamp(seg.end)
        time_tag = f"[{start_str} - {end_str}]"
        clean_text = seg.text.strip()
        
        if clean_text:
            segments.append({
                "index": i,
                "start": seg.start,
                "end": seg.end,
                "start_str": start_str,
                "end_str": end_str,
                "time_tag": time_tag,
                "text": clean_text,
            })
            formatted_lines.append(f"{time_tag} {clean_text}")
            plain_texts.append(clean_text)

        if progress_callback and duration > 0:
            pct = min(95, int(15 + (seg.end / duration) * 75))
            progress_callback(pct, f"Transcribing [{start_str}]...")

    full_transcript_formatted = "\n".join(formatted_lines)
    full_transcript_plain = " ".join(plain_texts)

    if progress_callback:
        progress_callback(95, "Finalizing transcription...")

    return {
        "text": full_transcript_plain,
        "formatted_text": full_transcript_formatted,
        "segments": segments,
        "language": detected_lang,
        "duration": duration,
    }

def transcribe_with_sarvam(wav_path: str, progress_callback=None) -> Dict[str, Any]:
    """
    Optional Sarvam API transcription for Hinglish / Indian languages.
    """
    if not SARVAM_API_KEY:
        raise RuntimeError("SARVAM_API_KEY is not set. Please add it to your .env file or use Whisper.")

    audio = AudioSegment.from_wav(wav_path)
    piece_ms = 25 * 1000
    total_pieces = (len(audio) + piece_ms - 1) // piece_ms

    plain_texts = []
    formatted_lines = []
    segments = []

    url = "https://api.sarvam.ai/speech-to-text-translate"
    headers = {"api-subscription-key": SARVAM_API_KEY}

    for i, start in enumerate(range(0, len(audio), piece_ms)):
        piece = audio[start: start + piece_ms]
        piece_path = f"{wav_path}_piece_{i}.wav"
        piece.export(piece_path, format="wav")

        try:
            if progress_callback:
                progress_callback(int((i / total_pieces) * 80) + 10, f"Translating chunk {i+1}/{total_pieces} via Sarvam...")

            with open(piece_path, "rb") as f:
                files = {"file": (os.path.basename(piece_path), f, "audio/wav")}
                data = {"model": SARVAM_STT_MODEL, "with_diarization": "false"}
                resp = requests.post(url, headers=headers, files=files, data=data, timeout=120)
                resp.raise_for_status()
                piece_text = resp.json().get("transcript", "").strip()

            if piece_text:
                start_sec = start / 1000.0
                end_sec = min(len(audio), start + piece_ms) / 1000.0
                time_tag = f"[{format_timestamp(start_sec)} - {format_timestamp(end_sec)}]"
                segments.append({
                    "index": i,
                    "start": start_sec,
                    "end": end_sec,
                    "start_str": format_timestamp(start_sec),
                    "end_str": format_timestamp(end_sec),
                    "time_tag": time_tag,
                    "text": piece_text,
                })
                formatted_lines.append(f"{time_tag} {piece_text}")
                plain_texts.append(piece_text)
        finally:
            if os.path.exists(piece_path):
                os.remove(piece_path)

    return {
        "text": " ".join(plain_texts),
        "formatted_text": "\n".join(formatted_lines),
        "segments": segments,
        "language": "hinglish",
        "duration": len(audio) / 1000.0,
    }

def transcribe_audio(
    wav_path: str,
    language: str = "english",
    model_size: str = WHISPER_MODEL,
    progress_callback=None,
) -> Dict[str, Any]:
    """
    Main transcription entrypoint.
    If 'hinglish' is requested AND SARVAM_API_KEY is available, uses Sarvam.
    Otherwise, uses local Faster-Whisper.
    """
    if language.lower() == "hinglish" and SARVAM_API_KEY:
        try:
            return transcribe_with_sarvam(wav_path, progress_callback=progress_callback)
        except Exception as e:
            print(f"[Transcriber] Sarvam API failed ({e}), falling back to Whisper...")
            return transcribe_with_whisper(wav_path, language=None, model_size=model_size, progress_callback=progress_callback)

    return transcribe_with_whisper(wav_path, language=language, model_size=model_size, progress_callback=progress_callback)
