"""Roda os laboratórios locais numa única aba, limpando cookie e storage entre etapas."""

from __future__ import annotations

import traceback

from pecas_e_prova.labs import (
    bordas,
    emulacao,
    espera,
    formulario,
    gravacao,
    hello,
    leitura,
    relogio,
    sessao,
)
from pecas_e_prova.session import fixture_server, headless_from_env, start_browser

LABS = [
    ("01 hello", hello.run),
    ("02 formulário", formulario.run),
    ("03 leitura", leitura.run),
    ("04 espera", espera.run),
    ("05 sessão", sessao.run),
    ("06 emulação", emulacao.run),
    ("07 bordas", bordas.run),
    ("08 relógio", relogio.run),
    ("09 gravação", gravacao.run),
]


def _mostrar(pagina) -> None:
    """Traz o Chrome para a frente. A janela nasce atrás do editor."""
    try:
        pagina.bring_to_front()
        pagina.set_window(x=80, y=40, width=1100, height=780, state="normal")
    except Exception:
        return


def main() -> int:
    falhas: list[tuple[str, BaseException]] = []
    visivel = not headless_from_env()
    with fixture_server() as base:
        print(f"fixtures em {base}")
        if visivel:
            print("Os cliques aparecem na janela Chrome for Testing. Deixe ela na frente do editor.")
        bro = start_browser()
        try:
            pagina = bro.page()
            if visivel:
                _mostrar(pagina)
                print("Uma janela só. Os cliques acontecem nela.")
            for nome, executar in LABS:
                print(f"\n== {nome} ==", flush=True)
                try:
                    try:
                        pagina.context.clear_cookies()
                        pagina.context.clear_storage()
                        pagina.set_viewport({"width": 1100, "height": 720})
                    except Exception:
                        pass
                    executar(pagina, base, bro)
                    if visivel:
                        pagina.wait(700)
                    print("ok", flush=True)
                except Exception as erro:
                    falhas.append((nome, erro))
                    print(f"falhou: {erro}", flush=True)
                    traceback.print_exc()
        finally:
            bro.stop()

    print(f"\n{len(LABS) - len(falhas)}/{len(LABS)} laboratórios ok")
    if falhas:
        print("Falhas: " + ", ".join(nome for nome, _ in falhas))
        return 1
    return 0
