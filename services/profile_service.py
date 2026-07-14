"""Aggregates profile discovery across every registered browser service."""
from __future__ import annotations

from typing import Dict, List, Optional

import config
from services.base_service import BrowserProfile, ChromiumBrowserService
from services.brave_service import BraveService
from services.chrome_service import ChromeService
from services.edge_service import EdgeService
from utils.logger import get_logger

logger = get_logger(__name__)


class ProfileService:
    """Central registry of browser services and the profiles they expose.

    To support a new Chromium-based browser, add its service instance to
    ``_services`` below (and a matching entry in ``config.py``). Nothing
    else in the application needs to change.
    """

    def __init__(self) -> None:
        self._services: Dict[str, ChromiumBrowserService] = {
            "chrome": ChromeService(),
            "edge": EdgeService(),
            "brave": BraveService(),
        }

    def get_service(self, browser_id: str) -> Optional[ChromiumBrowserService]:
        return self._services.get(browser_id)

    def get_installed_browsers(self) -> List[str]:
        return [bid for bid, svc in self._services.items() if svc.is_installed()]

    def get_all_profiles(self) -> List[BrowserProfile]:
        """Return every discovered profile across all supported browsers."""
        profiles: List[BrowserProfile] = []
        for browser_id in config.SUPPORTED_BROWSER_IDS:
            service = self._services.get(browser_id)
            if not service:
                continue
            try:
                profiles.extend(service.get_profiles())
            except Exception:  # noqa: BLE001 - never let one browser break the rest
                logger.exception("Failed to read profiles for browser '%s'", browser_id)
        return profiles


# Module-level singleton used by the Flask routes.
profile_service = ProfileService()
