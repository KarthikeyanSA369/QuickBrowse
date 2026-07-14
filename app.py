"""Browser Profile Manager — application entry point.

Starts the local Flask API/UI server in a background thread and hosts it
inside a native PyWebView desktop window. This file intentionally stays
thin: all real logic lives in ``backend/`` and ``services/``.
"""
from __future__ import annotations

import socket
import sys
import threading
import time

import webview

import config
from backend.app_factory import create_app
from utils.logger import get_logger

logger = get_logger(__name__)


def _port_is_free(host: str, port: int) -> bool:
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        return sock.connect_ex((host, port)) != 0


def _pick_port(host: str, preferred: int) -> int:
    if _port_is_free(host, preferred):
        return preferred
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as sock:
        sock.bind((host, 0))
        return sock.getsockname()[1]


def _run_server(app, host: str, port: int) -> None:
    try:
        app.run(host=host, port=port, debug=False, use_reloader=False, threaded=True)
    except Exception:  # noqa: BLE001
        logger.exception("Flask server crashed")


def _wait_for_server(host: str, port: int, timeout: float = 10.0) -> bool:
    deadline = time.time() + timeout
    while time.time() < deadline:
        if not _port_is_free(host, port):
            return True
        time.sleep(0.1)
    return False


def main() -> int:
    logger.info("Starting %s v%s", config.APP_NAME, config.APP_VERSION)

    host = config.FLASK_HOST
    port = _pick_port(host, config.FLASK_PORT)

    app = create_app()
    server_thread = threading.Thread(
        target=_run_server, args=(app, host, port), daemon=True, name="flask-server"
    )
    server_thread.start()

    if not _wait_for_server(host, port):
        logger.error("Local server failed to start on %s:%s", host, port)
        return 1

    url = f"http://{host}:{port}/"
    logger.info("Serving UI from %s", url)

    window = webview.create_window(
        config.WINDOW_TITLE,
        url,
        width=config.WINDOW_WIDTH,
        height=config.WINDOW_HEIGHT,
        min_size=(config.WINDOW_MIN_WIDTH, config.WINDOW_MIN_HEIGHT),
        resizable=True,
        text_select=False,
    )
    window.events.loaded += lambda: window.evaluate_js("""
    setTimeout(() => {
        const s = document.getElementById('search-input');
        if (s) {
            s.focus();
            s.click();
        }
    }, 500);
    """)
    try:
        webview.start()
    except Exception:  # noqa: BLE001
        logger.exception("PyWebView window crashed")
        return 1

    logger.info("%s closed", config.APP_NAME)
    return 0


if __name__ == "__main__":
    sys.exit(main())
