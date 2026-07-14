"""Launching browser profiles and opening their folders on disk."""
from __future__ import annotations

import subprocess
from dataclasses import dataclass
from typing import Optional

from services.profile_service import ProfileService
from utils.logger import get_logger
from utils.paths import open_in_file_explorer

logger = get_logger(__name__)


@dataclass
class LaunchResult:
    success: bool
    message: str


class LauncherService:
    """Resolves a profile id (e.g. 'chrome:Default') into a running process."""

    def __init__(self, profile_service: ProfileService) -> None:
        self._profile_service = profile_service

    def _split_profile_id(self, profile_id: str):
        if ":" not in profile_id:
            return None, None
        browser_id, profile_dir = profile_id.split(":", 1)
        return browser_id, profile_dir

    def launch(self, profile_id: str) -> LaunchResult:
        browser_id, profile_dir = self._split_profile_id(profile_id)
        if not browser_id or not profile_dir:
            return LaunchResult(False, f"Invalid profile id: '{profile_id}'")

        service = self._profile_service.get_service(browser_id)
        if not service:
            return LaunchResult(False, f"Unsupported browser: '{browser_id}'")

        executable = service.resolve_executable()
        if not executable:
            return LaunchResult(
                False,
                f"Could not find an installed executable for {service.display_name}.",
            )

        try:
            creationflags = 0
            if hasattr(subprocess, "CREATE_NO_WINDOW"):
                creationflags = subprocess.CREATE_NO_WINDOW  # type: ignore[attr-defined]

            subprocess.Popen(
                [str(executable), f"--profile-directory={profile_dir}"],
                creationflags=creationflags,
                close_fds=True,
            )
            logger.info("Launched %s profile '%s'", service.display_name, profile_dir)
            return LaunchResult(True, f"Launched {service.display_name} ({profile_dir}).")
        except OSError as exc:
            logger.error("Failed to launch %s profile '%s': %s", browser_id, profile_dir, exc)
            return LaunchResult(False, f"Failed to launch profile: {exc}")

    def open_folder(self, profile_id: str) -> LaunchResult:
        browser_id, profile_dir = self._split_profile_id(profile_id)
        if not browser_id or not profile_dir:
            return LaunchResult(False, f"Invalid profile id: '{profile_id}'")

        service = self._profile_service.get_service(browser_id)
        if not service:
            return LaunchResult(False, f"Unsupported browser: '{browser_id}'")

        folder = service.get_profile_folder(profile_dir)
        if open_in_file_explorer(folder):
            return LaunchResult(True, f"Opened folder for {service.display_name} ({profile_dir}).")
        return LaunchResult(False, f"Could not open folder: {folder}")
