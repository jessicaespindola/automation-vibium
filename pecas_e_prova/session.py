"""Browser visível por padrão e um servidor local das fixtures."""

from __future__ import annotations

import os
import threading
from contextlib import contextmanager
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer

from vibium import browser

from pecas_e_prova.paths import EVIDENCE, FIXTURES


def headless_from_env() -> bool:
    return os.environ.get("PECAS_HEADLESS", "").strip().lower() in {"1", "true", "yes"}


class _Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FIXTURES), **kwargs)

    def log_message(self, format: str, *args) -> None:
        return


@contextmanager
def fixture_server(port: int = 0):
    """Sobe as páginas de fixtures em 127.0.0.1. Porta 0 escolhe uma porta livre."""
    httpd = ThreadingHTTPServer(("127.0.0.1", port), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    host, port = httpd.server_address
    try:
        yield f"http://{host}:{port}"
    finally:
        httpd.shutdown()
        thread.join(timeout=3)


def start_browser():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    return browser.start(headless=headless_from_env())
