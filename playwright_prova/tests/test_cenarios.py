"""Os mesmos nove roteiros da suíte Vibium, no idioma do Playwright.

Locators por papel, rótulo e test id. Asserções com expect, que espera sozinho.
Sem sleep. Contexto novo por teste, vindo do pytest-playwright.
"""

import re
from pathlib import Path

from playwright.sync_api import expect

from conftest import EVIDENCE, FIXTURES


def test_01_hello(page):
    page.goto("/index.html")
    expect(page).to_have_title("Peças & Prova")
    page.screenshot(path=EVIDENCE / "01-hello.png")
    loja = page.get_by_role("link", name="Loja", exact=True)
    expect(loja).to_have_attribute("href", "loja.html")
    loja.click()
    expect(page).to_have_url(re.compile(r"loja\.html$"))
    expect(page.get_by_role("link", name="Battery Pack Local")).to_have_text("Battery Pack Local")


def test_02_formulario(page):
    page.goto("/formulario.html")
    page.get_by_test_id("salvar").click()
    expect(page.get_by_test_id("resumo")).to_have_text(
        "Não foi possível salvar. Corrija os campos abaixo."
    )
    expect(page.get_by_test_id("erro-email")).to_have_text("Informe o e-mail.")
    expect(page.get_by_test_id("erro-busca")).to_have_text("Informe o número de série.")
    expect(page.get_by_test_id("erro-pais")).to_have_text("Escolha o país.")
    expect(page.get_by_test_id("erro-termo")).to_have_text("Aceite o termo de serviço.")
    expect(page.get_by_test_id("resultado")).to_have_text("")

    page.get_by_label("E-mail").fill("ana")
    page.get_by_test_id("salvar").click()
    expect(page.get_by_test_id("erro-email")).to_have_text("E-mail inválido.")
    expect(page.get_by_test_id("aviso")).to_have_text("")

    page.get_by_label("E-mail").fill("ana@exemplo.com")
    page.get_by_placeholder("número de série").fill("VAR-347")
    page.get_by_label("País").select_option("Brasil")
    termo = page.get_by_role("checkbox", name="Aceito o termo de serviço")
    termo.check()
    expect(termo).to_be_checked()
    nota = page.get_by_test_id("nota")
    nota.fill("baia")
    nota.press_sequentially(" 14-C")
    expect(nota).to_have_value("baia 14-C")
    page.get_by_test_id("salvar").click()
    expect(page.get_by_test_id("aviso")).to_have_text("Ficha salva.")
    expect(page.get_by_test_id("erro-email")).to_have_text("")
    expect(page.get_by_test_id("resultado")).to_have_text("ana@exemplo.com|Brasil|sim")
    termo.uncheck()
    expect(termo).not_to_be_checked()


def test_03_leitura(page):
    page.goto("/acessivel.html")
    expect(page.get_by_text("14-C")).to_contain_text("14-C")
    expect(page).to_have_title("Acessibilidade")
    botao = page.get_by_role("button", name="Consultar série")
    expect(botao).to_have_text("Consultar série")
    logo = page.get_by_role("img", name="Logo da oficina")
    expect(logo).to_have_attribute("alt", "Logo da oficina")
    page.screenshot(path=EVIDENCE / "04-acessivel.png", full_page=True)
    page.pdf(path=EVIDENCE / "04-acessivel.pdf")
    mensagens = []
    page.on("console", lambda msg: mensagens.append(msg.text))
    page.evaluate("console.log('peca-ok')")
    assert "peca-ok" in mensagens


def test_04_espera(page):
    page.goto("/espera.html")
    seguir = page.get_by_test_id("seguir")
    expect(seguir).to_be_disabled()
    page.get_by_test_id("armar").click()
    expect(page.get_by_test_id("estado")).to_have_text("pronto")
    expect(seguir).to_be_enabled()


def test_05_sessao(page, context, app_url, browser):
    page.goto("/formulario.html")
    context.add_cookies([{"name": "bay", "value": "14-C", "url": app_url + "/"}])
    page.evaluate("localStorage.setItem('unidade', 'VAR-347')")
    page.reload()
    cookies = context.cookies()
    assert any(item["name"] == "bay" and item["value"] == "14-C" for item in cookies)
    assert page.evaluate("localStorage.getItem('unidade')") == "VAR-347"

    comprador = browser.new_context()
    visitante = browser.new_context()
    try:
        pagina_comprador = comprador.new_page()
        pagina_visitante = visitante.new_page()
        pagina_comprador.goto(app_url + "/loja.html")
        pagina_visitante.goto(app_url + "/loja.html")
        pagina_comprador.evaluate("localStorage.setItem('quem', 'comprador')")
        pagina_visitante.evaluate("localStorage.setItem('quem', 'visitante')")
        assert pagina_comprador.evaluate("localStorage.getItem('quem')") == "comprador"
        assert pagina_visitante.evaluate("localStorage.getItem('quem')") == "visitante"
    finally:
        comprador.close()
        visitante.close()


def test_06_emulacao(page, context):
    page.set_viewport_size({"width": 390, "height": 844})
    tamanho = page.viewport_size
    assert tamanho["width"] == 390 and tamanho["height"] == 844

    page.emulate_media(color_scheme="dark", reduced_motion="reduce", media="screen")
    page.goto("/midia.html")
    page.get_by_test_id("ler").click()
    expect(page.get_by_test_id("esquema")).to_have_text("dark")

    context.set_geolocation({"latitude": -23.55, "longitude": -46.63, "accuracy": 10})
    context.grant_permissions(["geolocation"])
    page.goto("/geo.html")
    page.get_by_test_id("ler").click()
    expect(page.get_by_test_id("lat")).to_have_text("-23.55")


def test_07_bordas(page):
    vistos = []

    def despachar(dialog):
        vistos.append((dialog.type, dialog.message))
        if dialog.type == "prompt":
            dialog.accept("14-C")
        else:
            dialog.accept()

    page.on("dialog", despachar)
    page.goto("/dialogo.html")
    page.get_by_test_id("alerta").click()
    expect(page.get_by_test_id("eco")).to_have_text("alerta-ok")
    assert vistos[0] == ("alert", "peca reservada")

    page.get_by_test_id("confirma").click()
    expect(page.get_by_test_id("eco")).to_have_text("confirmado")

    page.get_by_test_id("pergunta").click()
    expect(page.get_by_test_id("eco")).to_have_text("14-C")

    page.goto("/frames.html")
    painel = page.frame_locator('iframe[name="painel"]')
    expect(painel.locator("p")).to_have_text("peca interna")

    page.goto("/sombra.html")
    expect(page.locator("my-card").locator("#miolo")).to_have_text("texto na sombra")

    page.goto("/upload.html")
    page.get_by_test_id("arquivo").set_input_files(FIXTURES / "arquivos" / "peca.txt")
    expect(page.get_by_test_id("nome")).to_have_text("peca.txt")

    page.goto("/download.html")
    expect(page.get_by_test_id("baixar")).to_have_attribute("href", "arquivos/nota.txt")
    with page.expect_download() as captura:
        page.get_by_test_id("baixar").click()
    arquivo = captura.value.path()
    assert arquivo is not None
    assert "VAR-347" in Path(arquivo).read_text(encoding="utf-8")

    page.goto("/arraste.html")
    page.get_by_test_id("peca").drag_to(page.get_by_test_id("slot"))
    expect(page.get_by_test_id("slot")).to_have_text("encaixada")

    page.goto("/ponteiro.html")
    alvo = page.get_by_test_id("alvo")
    caixa = alvo.bounding_box()
    assert caixa is not None
    page.mouse.click(caixa["x"] + caixa["width"] / 2, caixa["y"] + caixa["height"] / 2)
    expect(page.get_by_test_id("eco")).to_have_text("clique-coordenada")

    toque = page.get_by_test_id("toque")
    caixa_toque = toque.bounding_box()
    assert caixa_toque is not None
    page.touchscreen.tap(
        caixa_toque["x"] + caixa_toque["width"] / 2,
        caixa_toque["y"] + caixa_toque["height"] / 2,
    )
    expect(page.get_by_test_id("eco")).to_have_text("toque-coordenada")

    campo = page.get_by_test_id("comando")
    campo.click()
    campo.press_sequentially("VAR-347")
    campo.press("Enter")
    expect(page.get_by_test_id("eco")).to_have_text("VAR-347")


def test_08_relogio(page):
    page.clock.install()
    page.goto("/relogio.html")
    page.get_by_test_id("armar").click()
    expect(page.get_by_test_id("estado")).to_have_text("aguardando")
    page.clock.fast_forward(5000)
    expect(page.get_by_test_id("estado")).to_have_text("disparou")


def test_09_gravacao(page, context):
    destino = EVIDENCE / "loja.zip"
    context.tracing.start(screenshots=True, snapshots=True)
    try:
        page.goto("/loja.html")
        page.get_by_role("link", name="Battery Pack Local").click()
        page.get_by_role("button", name="Adicionar ao carrinho").click()
        expect(page.get_by_test_id("contagem")).to_have_text("1")
    finally:
        context.tracing.stop(path=destino)
    assert destino.is_file()
    assert destino.stat().st_size > 0
