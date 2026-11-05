"""Fluxo go → map → @ref → diff, que existe na CLI e no MCP, não no client Python."""

from __future__ import annotations

import os
import re
import subprocess

from pecas_e_prova.paths import EVIDENCE
from pecas_e_prova.session import fixture_server, headless_from_env


def _binario() -> str:
    """O `vibium` do pip 26.8.21 só encaminha install e version.

    go, map e diff estão no binário que o client usa por baixo.
    """
    from vibium.binary import find_vibium_bin

    return find_vibium_bin()


def _rodar(binario: str, argumentos: list[str], ambiente: dict[str, str]) -> str:
    if headless_from_env():
        argumentos = ["--headless", *argumentos]
    concluido = subprocess.run(
        [binario, *argumentos],
        env=ambiente,
        capture_output=True,
        text=True,
        encoding="utf-8",
        errors="replace",
        timeout=120,
    )
    saida = (concluido.stdout or "") + (concluido.stderr or "")
    if concluido.returncode != 0:
        raise RuntimeError(f"vibium {' '.join(argumentos)} falhou:\n{saida}")
    return saida


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    binario = _binario()
    ambiente = os.environ.copy()
    ambiente["VIBIUM_SESSION"] = "pecas-mapa"
    try:
        with fixture_server() as base:
            _rodar(binario, ["go", f"{base}/loja.html"], ambiente)
            mapa = _rodar(binario, ["map"], ambiente)
            (EVIDENCE / "mapa.txt").write_text(mapa, encoding="utf-8")
            if "Battery Pack Local" not in mapa and "Adicionar" not in mapa:
                raise RuntimeError(f"o mapa não mostrou a loja:\n{mapa}")
            achado = _rodar(binario, ["find", "text", "Adicionar ao carrinho"], ambiente)
            referencia = re.search(r"@e\d+", achado)
            if referencia is None:
                raise RuntimeError(f"find não devolveu @ref:\n{achado}")
            _rodar(binario, ["click", referencia.group(0)], ambiente)
            diff = _rodar(binario, ["diff", "map"], ambiente)
            (EVIDENCE / "diff-mapa.txt").write_text(diff, encoding="utf-8")
            texto = _rodar(binario, ["text", "[data-testid=contagem]"], ambiente)
            if texto.strip() != "1":
                raise RuntimeError(f"o carrinho não mudou para 1:\n{texto}")
            _rodar(binario, ["screenshot", "-o", str(EVIDENCE / "mapa.png")], ambiente)
        print(f"ok — mapa em {EVIDENCE / 'mapa.txt'}")
        return 0
    finally:
        subprocess.run(
            [binario, "daemon", "stop"],
            env=ambiente,
            capture_output=True,
            text=True,
            timeout=30,
        )
