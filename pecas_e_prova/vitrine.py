"""Checkout em https://var.parts, o fluxo publicado no tutorial de gravação do Vibium.

Chrome não grava a faixa de vídeo. Para o WebM, use o comando video, com Firefox 154+.
"""

from pecas_e_prova.expect import expect
from pecas_e_prova.paths import EVIDENCE
from pecas_e_prova.session import start_browser


def main() -> int:
    EVIDENCE.mkdir(parents=True, exist_ok=True)
    bro = start_browser()
    try:
        vibe = bro.page()
        gravacao = vibe.context.recording
        destino = EVIDENCE / "var-parts.zip"
        gravacao.start(name="checkout", path=str(destino), video=False)
        try:
            vibe.go("https://var.parts")
            gravacao.start_group("escolher peca")
            vibe.find(text="Vibium Battery Pack").click()
            vibe.find(role="button", text="Add to Cart").click()
            gravacao.stop_group()

            gravacao.start_group("pagar")
            vibe.find('a[href="/cart"]').click()
            vibe.find(role="button", text="Proceed to Checkout").click()
            vibe.find(label="Unit Designation").fill("VAR-347")
            vibe.find(label="Service Bay").fill("Bay 14-C")
            vibe.find(text="Lunar VAR Facility").click()
            vibe.find(role="button", text="Proceed to Payment").click()
            gravacao.stop_group()

            corpo = vibe.evaluate("document.body.innerText")
            (EVIDENCE / "var-parts.txt").write_text(corpo, encoding="utf-8")
            (EVIDENCE / "var-parts.png").write_bytes(vibe.screenshot(full_page=True))
            expect(
                any(trecho in corpo for trecho in ("VAR-347", "Battery", "Payment", "Order")),
                corpo[:500],
            )
        finally:
            resultado = gravacao.stop()
            print(resultado)
        expect(destino.is_file(), "a gravação do checkout não foi escrita")
        print(f"ok — abra {destino} em https://player.vibium.dev")
        return 0
    finally:
        bro.stop()
