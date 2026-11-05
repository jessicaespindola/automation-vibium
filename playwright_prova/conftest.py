"""Sobe as mesmas fixtures do Vibium e entrega a base_url ao Playwright.

Cada teste ganha um contexto novo. Essa é a prática do Playwright: cookie e
storage não vazam de um roteiro para o outro. A suíte Vibium reusa uma aba.
"""

from __future__ import annotations

import threading
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[1]
FIXTURES = ROOT / "fixtures"
EVIDENCE = ROOT / "evidence" / "playwright"


class _Handler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=str(FIXTURES), **kwargs)

    def log_message(self, format: str, *args) -> None:
        return


@pytest.fixture(scope="session")
def app_url():
    httpd = ThreadingHTTPServer(("127.0.0.1", 0), _Handler)
    thread = threading.Thread(target=httpd.serve_forever, daemon=True)
    thread.start()
    _host, port = httpd.server_address
    try:
        yield f"http://127.0.0.1:{port}"
    finally:
        httpd.shutdown()
        thread.join(timeout=3)


@pytest.fixture(scope="session")
def browser_context_args(browser_context_args, app_url):
    # has_touch liga o touchscreen. Sem isso, tap() recusa o contexto.
    return {**browser_context_args, "base_url": app_url, "has_touch": True}


@pytest.fixture(scope="session", autouse=True)
def _evidence_dir():
    EVIDENCE.mkdir(parents=True, exist_ok=True)
