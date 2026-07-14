"""
Application-wide configuration and constants for Browser Profile Manager.

This module centralizes every path, size, and constant used across the
application so that behavior can be tuned from a single location.
"""
from __future__ import annotations

import os
from pathlib import Path
from typing import Dict, List

# ---------------------------------------------------------------------------
# Application metadata
# ---------------------------------------------------------------------------
APP_NAME = "Browser Profile Manager"
APP_VERSION = "1.0.0"
APP_AUTHOR = "Browser Profile Manager Team"
APP_DESCRIPTION = (
    "Discover, search, and launch browser profiles from Chrome, Edge, "
    "and Brave in one unified interface."
)

# ---------------------------------------------------------------------------
# Window configuration
# ---------------------------------------------------------------------------
WINDOW_WIDTH = 1280
WINDOW_HEIGHT = 800
WINDOW_MIN_WIDTH = 1000
WINDOW_MIN_HEIGHT = 650
WINDOW_TITLE = APP_NAME

# ---------------------------------------------------------------------------
# Local web server configuration (served internally, never exposed publicly)
# ---------------------------------------------------------------------------
FLASK_HOST = "127.0.0.1"
FLASK_PORT = 5679
DEBUG = False


def _local_app_data() -> Path:
    """Return the Windows LOCALAPPDATA directory, with a safe fallback."""
    local_app_data = os.environ.get("LOCALAPPDATA")
    if local_app_data:
        return Path(local_app_data)
    # Fallback for non-Windows environments (development / testing only).
    return Path.home() / "AppData" / "Local"


def _program_files_dirs() -> List[Path]:
    """Return the set of Program Files roots to search for executables."""
    candidates = []
    for env_var in ("ProgramFiles", "ProgramFiles(x86)", "ProgramW6432"):
        value = os.environ.get(env_var)
        if value:
            candidates.append(Path(value))
    if not candidates:
        candidates = [Path("C:/Program Files"), Path("C:/Program Files (x86)")]
    return candidates


# ---------------------------------------------------------------------------
# User data — NEVER stored inside Program Files. Everything writable lives
# under %LOCALAPPDATA%/BrowserProfileManager.
# ---------------------------------------------------------------------------
USER_DATA_DIR = _local_app_data() / "BrowserProfileManager"
CACHE_DIR = USER_DATA_DIR / "cache"
AVATAR_CACHE_DIR = CACHE_DIR / "avatars"
LOGS_DIR = USER_DATA_DIR / "logs"
SETTINGS_FILE = USER_DATA_DIR / "settings.json"
PERMISSION_FILE = USER_DATA_DIR / "permission.json"

for _directory in (USER_DATA_DIR, CACHE_DIR, AVATAR_CACHE_DIR, LOGS_DIR):
    _directory.mkdir(parents=True, exist_ok=True)

# ---------------------------------------------------------------------------
# Browser discovery configuration.
#
# The architecture is intentionally data-driven: adding a new Chromium-based
# browser (Opera, Vivaldi, Arc, plain Chromium, ...) only requires adding a
# new entry here and a matching service subclass in services/.
# ---------------------------------------------------------------------------
_LOCAL = _local_app_data()
_PROGRAM_ROOTS = _program_files_dirs()

BROWSER_USER_DATA_PATHS: Dict[str, Path] = {
    "chrome": _LOCAL / "Google" / "Chrome" / "User Data",
    "edge": _LOCAL / "Microsoft" / "Edge" / "User Data",
    "brave": _LOCAL / "BraveSoftware" / "Brave-Browser" / "User Data",
}

BROWSER_EXECUTABLE_CANDIDATES: Dict[str, List[Path]] = {
    "chrome": [root / "Google" / "Chrome" / "Application" / "chrome.exe" for root in _PROGRAM_ROOTS]
    + [_LOCAL / "Google" / "Chrome" / "Application" / "chrome.exe"],
    "edge": [root / "Microsoft" / "Edge" / "Application" / "msedge.exe" for root in _PROGRAM_ROOTS],
    "brave": [root / "BraveSoftware" / "Brave-Browser" / "Application" / "brave.exe" for root in _PROGRAM_ROOTS]
    + [_LOCAL / "BraveSoftware" / "Brave-Browser" / "Application" / "brave.exe"],
}

BROWSER_DISPLAY_NAMES: Dict[str, str] = {
    "chrome": "Google Chrome",
    "edge": "Microsoft Edge",
    "brave": "Brave Browser",
}

# Filenames Chromium browsers use to cache a signed-in user's avatar image
# inside a profile directory. Checked in order; the first match wins.
AVATAR_CANDIDATE_FILENAMES: List[str] = [
    "Google Profile Picture.png",
    "Edge Profile Picture.png",
    "Profile Picture.png",
    "Avatar.png",
    "profile.ico",
]

# Ordered list of browser ids that ship in this build. Order here controls
# the order of filter pills and grid grouping.
SUPPORTED_BROWSER_IDS: List[str] = ["chrome", "edge", "brave"]
