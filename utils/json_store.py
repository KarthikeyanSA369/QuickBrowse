"""Small helper for reading and writing JSON files that live in user data.

Every read is defensive: a missing, empty, or corrupt file simply falls back
to the provided default instead of raising, since these files represent
best-effort local state (settings, permissions, caches).
"""
from __future__ import annotations

import json
from pathlib import Path
from typing import Any

from utils.logger import get_logger

logger = get_logger(__name__)


def read_json(path: Path, default: Any = None) -> Any:
    if not path.exists():
        return default
    try:
        with path.open("r", encoding="utf-8") as handle:
            return json.load(handle)
    except (json.JSONDecodeError, OSError) as exc:
        logger.warning("Failed to read JSON file %s: %s", path, exc)
        return default


def write_json(path: Path, data: Any) -> bool:
    try:
        path.parent.mkdir(parents=True, exist_ok=True)
        tmp_path = path.with_suffix(path.suffix + ".tmp")
        with tmp_path.open("w", encoding="utf-8") as handle:
            json.dump(data, handle, indent=2, ensure_ascii=False)
        tmp_path.replace(path)
        return True
    except OSError as exc:
        logger.error("Failed to write JSON file %s: %s", path, exc)
        return False
