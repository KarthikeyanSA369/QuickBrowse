"""Filesystem helpers for locating executables and avatar images."""
from __future__ import annotations

import os
import shutil
from pathlib import Path
from typing import Iterable, Optional

import config
from utils.logger import get_logger

logger = get_logger(__name__)


def resolve_executable(browser_id: str) -> Optional[Path]:
    """Locate the installed executable for a given browser id.

    Checks the well-known install locations first, then falls back to the
    system PATH via ``shutil.which`` so custom installs still work.
    """
    candidates: Iterable[Path] = config.BROWSER_EXECUTABLE_CANDIDATES.get(browser_id, [])
    for candidate in candidates:
        try:
            if candidate.exists():
                return candidate
        except OSError:
            continue

    which_names = {
        "chrome": "chrome",
        "edge": "msedge",
        "brave": "brave",
    }
    which_name = which_names.get(browser_id)
    if which_name:
        found = shutil.which(which_name)
        if found:
            return Path(found)

    logger.warning("Could not resolve executable for browser '%s'", browser_id)
    return None


def find_avatar_file(profile_dir: Path) -> Optional[Path]:
    """Look for a cached avatar image inside a browser profile directory."""
    if not profile_dir.exists():
        return None
    for filename in config.AVATAR_CANDIDATE_FILENAMES:
        candidate = profile_dir / filename
        if candidate.exists() and candidate.is_file():
            return candidate
    return None


def open_in_file_explorer(path: Path) -> bool:
    """Open a folder in the OS file explorer. Windows-first, with fallbacks."""
    try:
        if not path.exists():
            logger.warning("Cannot open folder, path does not exist: %s", path)
            return False
        if hasattr(os, "startfile"):
            os.startfile(str(path))  # type: ignore[attr-defined]
            return True
        if shutil.which("explorer"):
            os.system(f'explorer "{path}"')
            return True
        if shutil.which("open"):
            os.system(f'open "{path}"')
            return True
        if shutil.which("xdg-open"):
            os.system(f'xdg-open "{path}"')
            return True
    except OSError as exc:
        logger.error("Failed to open folder %s: %s", path, exc)
    return False
