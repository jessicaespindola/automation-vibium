"""Espera uma condição JavaScript e lê o estado do elemento."""

from pecas_e_prova.expect import expect


def run(page, base: str, bro) -> None:
    page.go(f"{base}/espera.html")
    seguir = page.find(testid="seguir")
    expect(seguir.is_enabled() is False, "o botao seguir deveria nascer desabilitado")
    page.find(testid="armar").click()
    page.wait_for_function("document.querySelector('[data-testid=estado]').textContent === 'pronto'")
    expect(page.find(testid="estado").text() == "pronto", "o sinal nao ficou pronto")
    expect(seguir.is_enabled() is True, "o botao seguir deveria habilitar")
    seguir.highlight()
