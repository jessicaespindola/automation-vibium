"""Run faz o objetivo. Check julga uma frase, com outro contexto de modelo.

Os dois pedem provedor configurado (`vibium ready ai`). O restante do
laboratório não usa modelo. Defina PECAS_RUN_CHECK=1 para executar de verdade.
"""

from __future__ import annotations

import os

from pecas_e_prova.paths import EVIDENCE
from pecas_e_prova.session import fixture_server, start_browser

RECEITA = """
Run e Check estão documentados no main do Vibium e ainda não existem
no pacote 26.8.21. Neste binário, `check` marca um checkbox.
`ready` e `run` não são comandos.

Quando o pacote passar a incluí-los, a receita da documentação é:

  $env:VIBIUM_AI_PROVIDER = "openai"
  $env:VIBIUM_AI_MODEL = "gpt-5.6-sol"
  $env:VIBIUM_AI_REASONING_EFFORT = "none"
  # a credencial fica na variável nativa do provedor, por exemplo OPENAI_API_KEY
  vibium ready ai

  vibium run "abra a loja local e adicione um Battery Pack Local ao carrinho" --keep-open
  vibium check "o carrinho contém exatamente um Battery Pack Local" -o evidence/check-ao-vivo.zip
  vibium check "durante a gravação o carrinho ficou com um Battery Pack Local" -i evidence/check-ao-vivo.zip --report evidence/veredito.json
  vibium stop

O veredito previsto é passed, failed ou inconclusive. Ele descreve a evidência
e não substitui a asserção determinística dos laboratórios.
"""


def _status(resultado) -> str | None:
    if isinstance(resultado, dict):
        return resultado.get("status")
    return getattr(resultado, "status", None)


def main() -> int:
    print(RECEITA.strip())
    from vibium.sync_api.browser import Browser

    if not hasattr(Browser, "run"):
        print(
            "\nO client instalado não tem Browser.run. "
            "A suíte determinística cobre o que o pacote 26.8.21 já faz."
        )
        return 0
    if os.environ.get("PECAS_RUN_CHECK", "").strip() != "1":
        print("\nPECAS_RUN_CHECK não está em 1. Nada foi enviado a um modelo.")
        return 0

    with fixture_server() as base:
        bro = start_browser()
        try:
            vibe = bro.page()
            feito = vibe.run(
                f"Open {base}/loja.html and add exactly one Battery Pack Local to the cart. "
                "Do not add any other product."
            )
            print("run:", feito)
            veredito = vibe.check("The cart contains exactly one Battery Pack Local")
            print("check:", veredito)
            arquivo = EVIDENCE / "loja.zip"
            if arquivo.is_file():
                from vibium import browser as lancador

                arquivo_veredito = lancador.check(
                    "During the recorded run the cart contained one Battery Pack Local",
                    record=str(arquivo),
                )
                print("check da gravação:", arquivo_veredito)
            if _status(feito) not in {"completed"} or _status(veredito) not in {"passed"}:
                return 1
            return 0
        finally:
            bro.stop()
