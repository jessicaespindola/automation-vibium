"""Relógio falso: avança 5 segundos sem esperar o tempo real."""

from pecas_e_prova.expect import expect


def run(page, base: str, bro) -> None:
    page.clock.install()
    page.go(f"{base}/relogio.html")
    page.find(testid="armar").click()
    expect(page.find(testid="estado").text() == "aguardando", "o timer nao deveria disparar na hora")
    page.clock.fast_forward(5000)
    page.wait_for_function(
        "document.querySelector('[data-testid=estado]').textContent === 'disparou'",
        timeout=3000,
    )
    expect(page.find(testid="estado").text() == "disparou", page.find(testid="estado").text())
    page.clock.resume()
