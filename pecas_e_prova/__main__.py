"""Entrada: python -m pecas_e_prova [suite|mapa|vitrine|agente|video]"""

from __future__ import annotations

import argparse
import os
import sys

from pecas_e_prova import agente, mapa, suite, ver, video, vitrine


def main() -> int:
    parser = argparse.ArgumentParser(description="Peças & Prova, laboratório Vibium")
    parser.add_argument(
        "comando",
        nargs="?",
        default="suite",
        choices=("ver", "suite", "mapa", "vitrine", "agente", "video"),
    )
    parser.add_argument("--headless", action="store_true", help="Esconde a janela do browser")
    args = parser.parse_args()
    if args.headless:
        os.environ["PECAS_HEADLESS"] = "1"
    comandos = {
        "ver": ver.main,
        "suite": suite.main,
        "mapa": mapa.main,
        "vitrine": vitrine.main,
        "agente": agente.main,
        "video": video.main,
    }
    return comandos[args.comando]()


if __name__ == "__main__":
    sys.exit(main())
