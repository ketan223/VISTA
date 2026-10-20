"""
VISTA AI Video Assistant - Media Acquisition & Audio Processing
Handles YouTube downloads via yt-dlp, local file uploads, audio extraction,
and conversion to 16kHz mono WAV for Whisper transcription.
"""

import os
import re
import shutil
import tempfile
from pathlib import Path
from typing import Dict, Any, Tuple
import yt_dlp
from pydub import AudioSegment

from config import (
    DOWNLOAD_DIR,
    UPLOAD_DIR,
    MAX_UPLOAD_SIZE_MB,
    ALLOWED_EXTENSIONS,
)

YOUTUBE_REGEX = re.compile(
    r"^(https?://)?(www\.)?(youtube\.com/watch\?v=|youtu\.be/|youtube\.com/shorts/|youtube\.com/embed/)[a-zA-Z0-9_-]+"
)

class MediaError(Exception):
    """Custom exception for media downloading, extraction, or validation issues."""
    pass

def is_valid_youtube_url(url: str) -> bool:
    if not url or not isinstance(url, str):
        return False
    return bool(YOUTUBE_REGEX.match(url.strip()))

def validate_local_file(file_path: str) -> Tuple[bool, str]:
    path = Path(file_path)
    if not path.exists():
        return False, f"File not found: {file_path}"
    
    ext = path.suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        return False, f"Unsupported file type '{ext}'. Allowed types: {', '.join(sorted(ALLOWED_EXTENSIONS))}"
    
    size_mb = path.stat().st_size / (1024 * 1024)
    if size_mb > MAX_UPLOAD_SIZE_MB:
        return False, f"File size ({size_mb:.1f} MB) exceeds maximum allowed limit of {MAX_UPLOAD_SIZE_MB} MB."
    
    return True, "Valid"

def download_youtube_media(url: str, progress_callback=None) -> Dict[str, Any]:
    """
    Download audio from YouTube and convert to 16kHz mono WAV using yt-dlp + FFmpeg.
    """
    if not is_valid_youtube_url(url):
        raise MediaError("Invalid YouTube URL. Please provide a valid YouTube watch, short, or share link.")

    target_base = DOWNLOAD_DIR / f"yt_{abs(hash(url)) % 10000000}"
    output_template = str(target_base) + ".%(ext)s"

    def _yt_progress(d):
        if progress_callback and d.get("status") == "downloading":
            total = d.get("total_bytes") or d.get("total_bytes_estimate") or 0
            downloaded = d.get("downloaded_bytes") or 0
            pct = (downloaded / total * 100) if total > 0 else 0
            progress_callback(pct, "Downloading YouTube stream...")

    ydl_opts = {
        "format": "bestaudio/best",
        "outtmpl": output_template,
        "socket_timeout": 25,
        "retries": 2,
        "postprocessors": [
            {
                "key": "FFmpegExtractAudio",
                "preferredcodec": "wav",
                "preferredquality": "192",
            }
        ],
        "postprocessor_args": [
            "-ar", "16000",
            "-ac", "1",
        ],
        "progress_hooks": [_yt_progress],
        "quiet": True,
        "no_warnings": True,
    }

    try:
        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            try:
                info = ydl.extract_info(url, download=True)
            except yt_dlp.utils.DownloadError as de:
                err_str = str(de)
                if "video is unavailable" in err_str.lower():
                    raise MediaError("This YouTube video is unavailable, private, or deleted. Please check the link or try another public video.")
                elif "sign in" in err_str.lower() or "bot" in err_str.lower():
                    raise MediaError("YouTube requires verification for this video. Please try another video or upload the file directly.")
                else:
                    raise MediaError(f"YouTube download error: {err_str}")
            
            title = info.get("title", "YouTube Video")
            duration = info.get("duration", 0)
            
            # The postprocessor generates .wav
            wav_path = str(target_base) + ".wav"
            if not os.path.exists(wav_path):
                # Search matching directory
                expected = ydl.prepare_filename(info)
                cand = os.path.splitext(expected)[0] + ".wav"
                if os.path.exists(cand):
                    wav_path = cand
                else:
                    raise MediaError("FFmpeg audio extraction failed to produce a valid WAV file.")

        return {
            "title": title,
            "duration": duration,
            "wav_path": wav_path,
            "source_type": "youtube",
            "source": url,
        }
    except Exception as e:
        if isinstance(e, MediaError):
            raise e
        raise MediaError(f"Failed to extract YouTube video: {str(e)}")

def convert_uploaded_file(file_obj, original_filename: str) -> Dict[str, Any]:
    """
    Saves uploaded file and converts it to a normalized 16kHz mono WAV file.
    """
    ext = Path(original_filename).suffix.lower()
    if ext not in ALLOWED_EXTENSIONS:
        raise MediaError(f"Unsupported format '{ext}'. Allowed: {', '.join(sorted(ALLOWED_EXTENSIONS))}")

    temp_input_path = UPLOAD_DIR / f"upload_{abs(hash(original_filename)) % 10000000}{ext}"
    with open(temp_input_path, "wb") as f:
        f.write(file_obj.getbuffer())

    valid, msg = validate_local_file(str(temp_input_path))
    if not valid:
        if temp_input_path.exists():
            temp_input_path.unlink()
        raise MediaError(msg)

    # Convert to 16kHz mono WAV
    output_wav_path = temp_input_path.with_suffix(".wav")
    try:
        audio = AudioSegment.from_file(str(temp_input_path))
        duration = len(audio) / 1000.0  # seconds
        audio = audio.set_channels(1).set_frame_rate(16000)
        audio.export(str(output_wav_path), format="wav")
    except Exception as e:
        raise MediaError(f"Failed to convert media file to WAV: {str(e)}")
    finally:
        if temp_input_path.exists() and temp_input_path != output_wav_path:
            try:
                temp_input_path.unlink()
            except Exception:
                pass

    return {
        "title": Path(original_filename).stem,
        "duration": duration,
        "wav_path": str(output_wav_path),
        "source_type": "upload",
        "source": original_filename,
    }

def chunk_audio_if_needed(wav_path: str, chunk_minutes: int = 10) -> list:
    """
    Optionally splits large WAV files into manageable chunks for speech processing.
    """
    audio = AudioSegment.from_wav(wav_path)
    chunk_ms = chunk_minutes * 60 * 1000
    
    if len(audio) <= chunk_ms:
        return [wav_path]

    chunks = []
    base_stem = Path(wav_path).stem
    parent_dir = Path(wav_path).parent

    for i, start in enumerate(range(0, len(audio), chunk_ms)):
        chunk = audio[start: start + chunk_ms]
        chunk_path = parent_dir / f"{base_stem}_chunk_{i}.wav"
        chunk.export(str(chunk_path), format="wav")
        chunks.append(str(chunk_path))

    return chunks
