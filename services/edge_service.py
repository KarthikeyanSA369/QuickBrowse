"""Microsoft Edge profile discovery service."""
from __future__ import annotations

from pathlib import Path

import config
from services.base_service import ChromiumBrowserService


class EdgeService(ChromiumBrowserService):
    @property
    def browser_id(self) -> str:
        return "edge"

    @property
    def display_name(self) -> str:
        return config.BROWSER_DISPLAY_NAMES["edge"]

    @property
    def user_data_dir(self) -> Path:
        return config.BROWSER_USER_DATA_PATHS["edge"]
