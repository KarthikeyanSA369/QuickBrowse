"""Tracks whether the user has granted permission to read browser profiles.

The decision is asked once on first launch and persisted locally so the
user is never prompted again unless they reset it from settings.
"""
from __future__ import annotations

from dataclasses import dataclass

import config
from utils.json_store import read_json, write_json
from utils.logger import get_logger

logger = get_logger(__name__)


@dataclass
class PermissionState:
    granted: bool
    decided: bool  # has the user ever answered the prompt?

    def to_dict(self) -> dict:
        return {"granted": self.granted, "decided": self.decided}


class PermissionService:
    def get_state(self) -> PermissionState:
        data = read_json(config.PERMISSION_FILE, default=None)
        if not data:
            return PermissionState(granted=False, decided=False)
        return PermissionState(
            granted=bool(data.get("granted", False)),
            decided=bool(data.get("decided", False)),
        )

    def set_granted(self, granted: bool) -> PermissionState:
        state = PermissionState(granted=granted, decided=True)
        if not write_json(config.PERMISSION_FILE, state.to_dict()):
            logger.error("Failed to persist permission decision")
        return state
