"""Mantém as páginas locais no ar e abre o navegador."""

from __future__ import annotations

import threading
import webbrowser

from pecas_e_prova.session import fixture_server

PORTA = 8765


def main() -> int:
    try:
        servidor = fixture_server(PORTA)
        base = servidor.__enter__()
    except OSError:
        servidor = fixture_server(0)
        base = servidor.__enter__()
    print(f"Peças & Prova no ar: {base}", flush=True)
    print("Deixe este terminal aberto. Ctrl+C encerra.", flush=True)
    webbrowser.open(base + "/")
    try:
        threading.Event().wait()
    except KeyboardInterrupt:
        print("encerrado")
    finally:
        servidor.__exit__(None, None, None)
    return 0
