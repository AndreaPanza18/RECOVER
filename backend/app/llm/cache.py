import os
import json
import hashlib
from typing import Optional, Dict, Any
from app.utils.env_loader import CACHE_DIR

# ============================================================
# CACHE SYSTEM
# ============================================================

def _cache_key(provider: str, prompt: str, params: Dict[str, Any]) -> str:

    raw = provider + prompt + json.dumps(params, sort_keys=True, ensure_ascii=False)
    return hashlib.sha256(raw.encode("utf-8")).hexdigest()


def _cache_path(key: str) -> str:
    return os.path.join(CACHE_DIR, f"{key}.json")


def load_from_cache(key: str) -> Optional[Dict[str, Any]]:

    path = _cache_path(key)

    if not os.path.exists(path):
        return None

    try:
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    except Exception:
        # Cache corrotta → ignorata
        return None


def save_to_cache(key: str, content: Dict[str, Any]) -> None:

    path = _cache_path(key)

    try:
        with open(path, "w", encoding="utf-8") as f:
            json.dump(content, f, ensure_ascii=False, indent=2)
    except Exception:
        # Non bloccare il programma se la cache fallisce
        pass
