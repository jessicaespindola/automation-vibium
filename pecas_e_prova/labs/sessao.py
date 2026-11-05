"""Cookie, localStorage, estado exportado e dois contextos isolados."""

import json

from pecas_e_prova.expect import expect
from pecas_e_prova.paths import EVIDENCE
from pecas_e_prova.session import headless_from_env


def run(page, base: str, bro) -> None:
    page.go(f"{base}/formulario.html")
    page.context.set_cookies([{"name": "bay", "value": "14-C", "url": f"{base}/"}])
    page.evaluate("localStorage.setItem('unidade', 'VAR-347')")
    page.reload()
    cookies = page.context.cookies()
    expect(any(item.get("name") == "bay" and item.get("value") == "14-C" for item in cookies), str(cookies))
    unidade = page.evaluate("localStorage.getItem('unidade')")
    expect(unidade == "VAR-347", str(unidade))
    estado = page.context.storage()
    (EVIDENCE / "estado.json").write_text(json.dumps(estado, indent=2, default=str), encoding="utf-8")

    if not headless_from_env():
        print("isolamento de duas janelas fica só no --headless, para a suíte visível usar uma janela")
        return

    comprador = bro.new_context()
    visitante = bro.new_context()
    try:
        pagina_comprador = comprador.new_page()
        pagina_visitante = visitante.new_page()
        pagina_comprador.go(f"{base}/loja.html")
        pagina_visitante.go(f"{base}/loja.html")
        pagina_comprador.evaluate("localStorage.setItem('quem', 'comprador')")
        pagina_visitante.evaluate("localStorage.setItem('quem', 'visitante')")
        expect(pagina_comprador.evaluate("localStorage.getItem('quem')") == "comprador", "contexto A vazou")
        expect(pagina_visitante.evaluate("localStorage.getItem('quem')") == "visitante", "contexto B vazou")
    finally:
        comprador.close()
        visitante.close()
