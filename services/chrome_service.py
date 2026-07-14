"""Google Chrome profile discovery service."""
from __future__ import annotations

from pathlib import Path

import config
from services.base_service import ChromiumBrowserService


class ChromeService(ChromiumBrowserService):
    @property
    def browser_id(self) -> str:
        return "chrome"

    @property
    def display_name(self) -> str:
        return config.BROWSER_DISPLAY_NAMES["chrome"]

    @property
    def user_data_dir(self) -> Path:
        return config.BROWSER_USER_DATA_PATHS["chrome"]
