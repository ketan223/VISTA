"""
VISTA Platform Configuration
Central configuration and runtime environment setup for VISTA and its modules.
"""

import os
import sys
from pathlib import Path
from dotenv import load_dotenv

# --- Python 3.13 & Windows Environment Patches ---
# 1. Prevent OpenMP duplicate initialization crash on Windows Anaconda
os.environ["KMP_DUPLICATE_LIB_OK"] = "TRUE"

# 2. Fix PEP 594 removal of audioop in Python 3.13 for pydub
try:
    import audioop  # noqa: F401
except ImportError:
    try:
        import audioop_lts as audioop
        sys.modules["audioop"] = audioop
    except ImportError:
        pass

# 3. Patch PyAV 19+ metadata_errors incompatibility with faster-whisper
try:
    import av
    _orig_av_open = av.open
    def _patched_av_open(*args, **kwargs):
        kwargs.pop("metadata_errors", None)
        return _orig_av_open(*args, **kwargs)
    av.open = _patched_av_open
except Exception:
    pass

# --- Root & Storage Paths ---
BASE_DIR = Path(__file__).resolve().parent
load_dotenv(BASE_DIR / ".env")

DATA_DIR = BASE_DIR / "data"
TEMP_DIR = BASE_DIR / "temp"

DOWNLOAD_DIR = TEMP_DIR / "downloads"
UPLOAD_DIR = TEMP_DIR / "uploads"
CACHE_DIR = DATA_DIR / "cache"
CHROMA_DIR = DATA_DIR / "chroma_db"

for directory in [DATA_DIR, TEMP_DIR, DOWNLOAD_DIR, UPLOAD_DIR, CACHE_DIR, CHROMA_DIR]:
    directory.mkdir(parents=True, exist_ok=True)

# --- Video Assistant Configurations ---
WHISPER_MODEL = os.getenv("WHISPER_MODEL", "base")  # "tiny", "base", "small", "medium"
WHISPER_DEVICE = os.getenv("WHISPER_DEVICE", "cpu")
WHISPER_COMPUTE_TYPE = os.getenv("WHISPER_COMPUTE_TYPE", "int8")

# LLM Selection & Fallbacks
LLM_PROVIDER = os.getenv("LLM_PROVIDER", "ollama")  # "ollama" or "mistral"
OLLAMA_BASE_URL = os.getenv("OLLAMA_BASE_URL", "http://localhost:11434")
OLLAMA_MODEL = os.getenv("OLLAMA_MODEL", "qwen2.5:1.5b")
MISTRAL_API_KEY = os.getenv("MISTRAL_API_KEY", "")
MISTRAL_MODEL = os.getenv("MISTRAL_MODEL", "mistral-small-latest")

# Sarvam (Optional cloud Hinglish API)
SARVAM_API_KEY = os.getenv("SARVAM_API_KEY", "")
SARVAM_STT_MODEL = os.getenv("SARVAM_STT_MODEL", "saaras:v2.5")

# RAG / Embeddings
EMBEDDING_MODEL_NAME = os.getenv("EMBEDDING_MODEL_NAME", "sentence-transformers/all-MiniLM-L6-v2")
CHROMA_COLLECTION_PREFIX = "vista_video_"

# Upload limits
MAX_UPLOAD_SIZE_MB = int(os.getenv("MAX_UPLOAD_SIZE_MB", "500"))
ALLOWED_EXTENSIONS = {
    ".mp4", ".mkv", ".avi", ".mov", ".webm",
    ".mp3", ".wav", ".m4a", ".aac", ".flac", ".ogg"
}
