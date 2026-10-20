"""
VISTA AI Video Assistant - Cache & Duplicate Manager
Tracks processed media items to avoid redundant downloads, extractions, and transcriptions.
"""

import hashlib
import json
import os
from pathlib import Path
from typing import Optional, Dict, Any
from config import CACHE_DIR

class CacheManager:
    @staticmethod
    def get_source_hash(source: str, is_file: bool = False) -> str:
        """
        Generate a unique deterministic hash for a given URL or file path/content.
        """
        hasher = hashlib.sha256()
        if is_file and os.path.exists(source):
            # Hash first 4MB and last 4MB + file size to quickly identify large files
            file_size = os.path.getsize(source)
            hasher.update(str(file_size).encode("utf-8"))
            hasher.update(Path(source).name.encode("utf-8"))
            with open(source, "rb") as f:
                hasher.update(f.read(4 * 1024 * 1024))
                if file_size > 8 * 1024 * 1024:
                    f.seek(-4 * 1024 * 1024, os.SEEK_END)
                    hasher.update(f.read(4 * 1024 * 1024))
        else:
            # Normalized URL string hash
            normalized_url = source.strip().lower()
            hasher.update(normalized_url.encode("utf-8"))

        return hasher.hexdigest()[:16]

    @staticmethod
    def get_cache_path(source_hash: str) -> Path:
        return CACHE_DIR / f"{source_hash}.json"

    @classmethod
    def load_cached_result(cls, source: str, is_file: bool = False) -> Optional[Dict[str, Any]]:
        source_hash = cls.get_source_hash(source, is_file=is_file)
        cache_file = cls.get_cache_path(source_hash)
        if cache_file.exists():
            try:
                with open(cache_file, "r", encoding="utf-8") as f:
                    data = json.load(f)
                    data["source_hash"] = source_hash
                    data["cached"] = True
                    return data
            except Exception as e:
                print(f"[CacheManager] Warning: failed to read cache {cache_file}: {e}")
        return None

    @classmethod
    def save_result(cls, source: str, result_data: Dict[str, Any], is_file: bool = False) -> str:
        source_hash = cls.get_source_hash(source, is_file=is_file)
        cache_file = cls.get_cache_path(source_hash)
        
        # Strip un-serializable objects (like rag_chain) before caching
        serializable = {
            k: v for k, v in result_data.items()
            if k not in ["rag_chain", "vector_store"]
        }
        serializable["source_hash"] = source_hash

        try:
            with open(cache_file, "w", encoding="utf-8") as f:
                json.dump(serializable, f, indent=2, ensure_ascii=False)
        except Exception as e:
            print(f"[CacheManager] Warning: failed to save cache {cache_file}: {e}")

        return source_hash
