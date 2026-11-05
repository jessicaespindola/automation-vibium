"""Busca semântica: label, placeholder, select, checkbox, fill e type."""

from pecas_e_prova.expect import expect


def _marcado(page) -> bool:
    return page.evaluate("document.getElementById('consentimento').checked") is True


def _definir(page, elemento, ligado: bool) -> None:
    """check/uncheck são idempotentes. O client 26.8.21 quebra os dois com
    SyntaxError: Identifier 'role' has already been declared. Nesse caso o
    clique só acontece se o estado ainda não for o desejado."""
    try:
        if ligado:
            elemento.check()
        else:
            elemento.uncheck()
        return
    except Exception as erro:
        if "role" not in str(erro):
            raise
    if _marcado(page) is not ligado:
        elemento.click()


def run(page, base: str, bro) -> None:
    page.go(f"{base}/formulario.html")
    page.find(testid="salvar").click()
    expect(
        page.find(testid="resumo").text() == "Não foi possível salvar. Corrija os campos abaixo.",
        page.find(testid="resumo").text(),
    )
    expect(page.find(testid="erro-email").text() == "Informe o e-mail.", page.find(testid="erro-email").text())
    expect(page.find(testid="erro-busca").text() == "Informe o número de série.", page.find(testid="erro-busca").text())
    expect(page.find(testid="erro-pais").text() == "Escolha o país.", page.find(testid="erro-pais").text())
    expect(page.find(testid="erro-termo").text() == "Aceite o termo de serviço.", page.find(testid="erro-termo").text())
    expect(page.find(testid="resultado").text() == "", "a ficha gravou sem dados")

    page.find(label="E-mail").fill("ana")
    page.find(testid="salvar").click()
    expect(page.find(testid="erro-email").text() == "E-mail inválido.", page.find(testid="erro-email").text())
    expect(page.find(testid="aviso").text() == "", "e-mail inválido não pode salvar")

    page.find(label="E-mail").fill("ana@exemplo.com")
    page.find(placeholder="número de série").fill("VAR-347")
    page.find(label="País").select_option("Brasil")
    consentimento = page.find(label="Aceito o termo de serviço")
    _definir(page, consentimento, True)
    expect(_marcado(page) is True, "checkbox nao ficou marcado")
    nota = page.find(testid="nota")
    nota.fill("baia")
    nota.type(" 14-C")
    expect(nota.value() == "baia 14-C", f"type deveria acrescentar: {nota.value()!r}")
    page.find(testid="salvar").click()
    expect(page.find(testid="aviso").text() == "Ficha salva.", page.find(testid="aviso").text())
    expect(page.find(testid="erro-email").text() == "", "o erro de e-mail ficou na tela")
    expect(
        page.find(testid="resultado").text() == "ana@exemplo.com|Brasil|sim",
        page.find(testid="resultado").text(),
    )
    _definir(page, consentimento, False)
    expect(_marcado(page) is False, "uncheck nao limpou o checkbox")
