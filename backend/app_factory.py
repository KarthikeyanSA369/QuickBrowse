"""Flask application factory."""
from __future__ import annotations

import sys
from pathlib import Path

from flask import Flask

import config
from backend.routes import api_bp
from utils.logger import get_logger

logger = get_logger(__name__)


def _resource_root() -> Path:
    """Return the base path for bundled resources.

    When frozen by PyInstaller, bundled data lives under ``sys._MEIPASS``.
    In development it's simply the project root.
    """
    if getattr(sys, "frozen", False) and hasattr(sys, "_MEIPASS"):
        return Path(sys._MEIPASS)  # type: ignore[attr-defined]
    return Path(__file__).resolve().parent.parent


def create_app() -> Flask:
    root = _resource_root()
    app = Flask(
        config.APP_NAME,
        template_folder=str(root / "templates"),
        static_folder=str(root / "static"),
        static_url_path="/static",
    )
    app.config["JSON_SORT_KEYS"] = False
    app.register_blueprint(api_bp)

    from flask import render_template

    @app.get("/")
    def index():
        return render_template("index.html", app_name=config.APP_NAME, version=config.APP_VERSION)

    @app.errorhandler(Exception)
    def handle_uncaught(exc):  # noqa: ANN001
        logger.exception("Unhandled application error")
        return {"error": "Unexpected server error. Check the logs for details."}, 500

    return app
