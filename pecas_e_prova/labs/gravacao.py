"""Grava o carrinho local em um zip compatível com o Record Player."""

from pecas_e_prova.expect import expect
from pecas_e_prova.paths import EVIDENCE


def run(page, base: str, bro) -> None:
    destino = EVIDENCE / "loja.zip"
    gravacao = page.context.recording
    gravacao.start(name="loja", path=str(destino), video=False)
    try:
        gravacao.start_group("escolher peca")
        page.go(f"{base}/loja.html")
        page.find(text="Battery Pack Local").click()
        page.find(role="button", text="Adicionar ao carrinho").click()
        gravacao.stop_group()
        expect(page.find(testid="contagem").text() == "1", "o carrinho local nao ficou com 1 item")
    finally:
        resultado = gravacao.stop()
    expect(destino.is_file(), f"gravacao nao escrita: {resultado}")
    expect(destino.stat().st_size > 0, "zip da gravacao ficou vazio")
