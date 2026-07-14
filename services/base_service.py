"""Base classes shared by every Chromium-based browser service.

Design notes
------------
All currently supported browsers (Chrome, Edge, Brave) are Chromium-based
and store profile metadata identically:

* ``User Data/Local State`` — a JSON file with a ``profile.info_cache``
  dict mapping profile directory name -> profile metadata (display name,
  Google account name, avatar hints, etc).
* ``User Data/<profile dir>/`` — the profile directory itself, which may
  contain a cached avatar image (see ``utils.paths.find_avatar_file``).

Because the logic is identical across browsers, ``ChromiumBrowserService``
implements it once. Adding a new Chromium-based browser (Opera, Vivaldi,
Arc, plain Chromium, ...) only requires a small subclass that supplies the
browser id, display name, user data directory, and executable candidates —
see ``services/chrome_service.py`` for a minimal example.
"""
from __future__ import annotations

from abc import ABC, abstractmethod
from dataclasses import dataclass
from pathlib import Path
from typing import Dict, List, Optional

from utils.logger import get_logger
from utils.json_store import read_json
from utils.paths import find_avatar_file, resolve_executable

logger = get_logger(__name__)


@dataclass
class BrowserProfile:
    """A single discovered browser profile."""

    id: str
    browser_id: str
    browser_name: str
    profile_dir: str
    name: str
    account_name: str
    user_data_dir: str

    def to_dict(self) -> dict:
        from urllib.parse import quote

        return {
            "id": self.id,
            "browserId": self.browser_id,
            "browserName": self.browser_name,
            "profileDir": self.profile_dir,
            "name": self.name,
            "accountName": self.account_name,
            "avatarUrl": f"/api/avatar/{self.browser_id}/{quote(self.profile_dir)}",
        }


class ChromiumBrowserService(ABC):
    """Shared discovery/launch logic for any Chromium-based browser."""

    # -- Required per-browser configuration ---------------------------------
    @property
    @abstractmethod
    def browser_id(self) -> str:
        """Stable machine identifier, e.g. 'chrome'."""

    @property
    @abstractmethod
    def display_name(self) -> str:
        """Human readable name, e.g. 'Google Chrome'."""

    @property
    @abstractmethod
    def user_data_dir(self) -> Path:
        """Absolute path to the browser's 'User Data' root."""

    # -- Shared behaviour -----------------------------------------------------
    def is_installed(self) -> bool:
        return self.user_data_dir.exists()

    def _local_state_path(self) -> Path:
        return self.user_data_dir / "Local State"

    def get_profiles(self) -> List[BrowserProfile]:
        """Discover every profile registered with this browser."""
        if not self.is_installed():
            return []

        local_state = read_json(self._local_state_path(), default={}) or {}
        info_cache: Dict[str, dict] = (
            local_state.get("profile", {}).get("info_cache", {}) or {}
        )

        if not info_cache:
            info_cache = self._fallback_scan_profile_dirs()

        profiles: List[BrowserProfile] = []
        for profile_dir, info in sorted(info_cache.items()):
            info = info or {}
            name = info.get("name") or info.get("shortcut_name") or profile_dir
            account_name = (
                info.get("user_name")
                or info.get("gaia_name")
                or info.get("gaia_given_name")
                or "Local profile"
            )
            profiles.append(
                BrowserProfile(
                    id=f"{self.browser_id}:{profile_dir}",
                    browser_id=self.browser_id,
                    browser_name=self.display_name,
                    profile_dir=profile_dir,
                    name=str(name),
                    account_name=str(account_name),
                    user_data_dir=str(self.user_data_dir),
                )
            )
        return profiles

    def _fallback_scan_profile_dirs(self) -> Dict[str, dict]:
        """Fallback discovery when 'Local State' is missing or unreadable.

        Scans for the conventional 'Default' and 'Profile N' directories so
        the app still finds something useful even if Chromium changes its
        Local State schema.
        """
        discovered: Dict[str, dict] = {}
        try:
            for entry in self.user_data_dir.iterdir():
                if entry.is_dir() and (entry.name == "Default" or entry.name.startswith("Profile ")):
                    discovered[entry.name] = {"name": entry.name}
        except OSError as exc:
            logger.warning("Failed to scan %s: %s", self.user_data_dir, exc)
        return discovered

    def get_avatar_path(self, profile_dir: str) -> Optional[Path]:
        return find_avatar_file(self.user_data_dir / profile_dir)

    def resolve_executable(self) -> Optional[Path]:
        return resolve_executable(self.browser_id)

    def get_profile_folder(self, profile_dir: str) -> Path:
        return self.user_data_dir / profile_dir
