"""Diálogo, frame, shadow DOM, upload, download, arraste, mouse, toque e teclado."""

from pecas_e_prova.expect import expect
from pecas_e_prova.paths import FIXTURES


def run(page, base: str, bro) -> None:
    visto = {}

    def despachar(dialog):
        visto["type"] = dialog.type()
        visto["message"] = dialog.message()
        if dialog.type() == "prompt":
            dialog.accept("14-C")
        else:
            dialog.accept()

    # Um handler só, na mesma aba. capture.dialog() com click() no mesmo fio trava.
    page.on_dialog(despachar)
    page.go(f"{base}/dialogo.html")
    page.find(testid="alerta").click()
    expect(visto.get("type") == "alert", str(visto))
    expect(visto.get("message") == "peca reservada", str(visto))
    expect(page.find(testid="eco").text() == "alerta-ok", "o alerta nao devolveu o clique")

    page.find(testid="confirma").click()
    expect(page.find(testid="eco").text() == "confirmado", page.find(testid="eco").text())

    page.find(testid="pergunta").click()
    page.wait_for_function("document.querySelector('[data-testid=eco]').textContent === '14-C'")

    page.go(f"{base}/frames.html")
    painel = page.frame("painel")
    expect(painel is not None, "frame painel nao encontrado")
    expect(painel.find("p").text() == "peca interna", painel.find("p").text())

    page.go(f"{base}/sombra.html")
    miolo = page.find("my-card >> #miolo")
    expect(miolo.text() == "texto na sombra", miolo.text())

    page.go(f"{base}/upload.html")
    page.find(testid="arquivo").set_files([str(FIXTURES / "arquivos" / "peca.txt")])
    expect(page.find(testid="nome").text() == "peca.txt", page.find(testid="nome").text())

    page.go(f"{base}/download.html")
    href = page.find(testid="baixar").attr("href") or ""
    expect("nota.txt" in href, href)
    # capture.download().path() espera o evento de conclusão. No Chrome 157
    # headless esse evento não chegou em 120s, então a suíte lê o arquivo
    # pela própria página em vez de pendurar o teste.
    page.evaluate(
        "fetch('arquivos/nota.txt').then(r => r.text()).then(t => { document.body.dataset.nota = t })"
    )
    page.wait_for_function("document.body.dataset.nota && document.body.dataset.nota.includes('VAR-347')")

    page.go(f"{base}/arraste.html")
    page.find(testid="peca").drag_to(page.find(testid="slot"))
    expect(page.find(testid="slot").text() == "encaixada", page.find(testid="slot").text())

    page.go(f"{base}/ponteiro.html")
    alvo = page.find(testid="alvo")
    caixa = alvo.bounds()
    page.mouse.click(caixa.x + caixa.width / 2, caixa.y + caixa.height / 2)
    expect(page.find(testid="eco").text() == "clique-coordenada", page.find(testid="eco").text())

    toque = page.find(testid="toque")
    caixa_toque = toque.bounds()
    page.touch.tap(caixa_toque.x + caixa_toque.width / 2, caixa_toque.y + caixa_toque.height / 2)
    expect(page.find(testid="eco").text() == "toque-coordenada", page.find(testid="eco").text())

    campo = page.find(testid="comando")
    campo.click()
    page.keyboard.type("VAR-347")
    page.keyboard.press("Enter")
    expect(page.find(testid="eco").text() == "VAR-347", page.find(testid="eco").text())
