"""Faixa de vídeo dentro do zip. Exige Firefox 154 ou mais novo.

No Chrome, `video=True` falha de propósito. Sem Firefox, este comando explica o erro e sai.
"""

from pecas_e_prova.expect import expect
from pecas_e_prova.paths import EVIDENCE
from pecas_e_prova.session import fixture_server, headless_from_env


def main() -> int:
    from vibium import firefox

    EVIDENCE.mkdir(parents=True, exist_ok=True)
    destino = EVIDENCE / "video.zip"
    with fixture_server() as base:
        bro = firefox.start(headless=headless_from_env())
        try:
            vibe = bro.page()
            gravacao = vibe.context.recording
            gravacao.start(name="video", path=str(destino), video=True)
            try:
                vibe.go(f"{base}/loja.html")
                vibe.find(role="button", text="Adicionar ao carrinho").click()
                expect(vibe.find(testid="contagem").text() == "1", "carrinho local sem 1 item")
            finally:
                resultado = gravacao.stop()
                print(resultado)
        finally:
            bro.stop()
    expect(destino.is_file(), "o zip com vídeo não foi escrito")
    print(f"ok — o WebM fica dentro de {destino}. Abra em https://player.vibium.dev")
    return 0
