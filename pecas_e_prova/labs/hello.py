"""Abre a página local, lê o título, tira screenshot e clica um link."""

from pecas_e_prova.expect import expect
from pecas_e_prova.paths import EVIDENCE


def run(page, base: str, bro) -> None:
    page.go(f"{base}/index.html")
    expect(page.title() == "Peças & Prova", f"titulo inesperado: {page.title()}")
    png = page.screenshot()
    (EVIDENCE / "01-hello.png").write_bytes(png)
    # Um seletor CSS no primeiro argumento faz o client ignorar text/label/role.
    link = page.find(text="Loja")
    expect("loja.html" in (link.attr("href") or ""), f"href inesperado: {link.attr('href')!r}")
    link.click()
    page.wait_for_url("loja.html")
    expect(page.find(text="Battery Pack Local").text() == "Battery Pack Local", "a loja nao abriu")
