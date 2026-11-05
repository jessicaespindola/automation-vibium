"""Texto, JavaScript, árvore de acessibilidade, screenshot e PDF."""

from pecas_e_prova.expect import expect
from pecas_e_prova.paths import EVIDENCE


def _papeis(node):
    if isinstance(node, dict):
        papel = node.get("role")
        if papel:
            yield papel
        for child in node.get("children") or []:
            yield from _papeis(child)


def _nomes(node):
    if isinstance(node, dict):
        name = node.get("name") or ""
        if name:
            yield name
        for child in node.get("children") or []:
            yield from _nomes(child)


def run(page, base: str, bro) -> None:
    page.go(f"{base}/acessivel.html")
    texto = page.find(text="14-C").text()
    expect("14-C" in texto, texto)
    titulo = page.evaluate("document.title")
    expect(titulo == "Acessibilidade", str(titulo))
    arvore = page.a11y_tree()
    nomes = " ".join(_nomes(arvore))
    papeis = _papeis(arvore)
    expect(arvore.get("name") == "Acessibilidade", str(arvore))
    expect("button" in papeis, str(arvore))
    expect("Logo da oficina" in nomes, nomes)
    botao = page.find(role="button", text="Consultar série")
    expect(botao.text() == "Consultar série", botao.text())
    logo = page.find(alt="Logo da oficina")
    expect(logo.attr("alt") == "Logo da oficina", "alt da imagem nao confere")
    (EVIDENCE / "04-acessivel.png").write_bytes(page.screenshot(full_page=True))
    (EVIDENCE / "04-acessivel.pdf").write_bytes(page.pdf())
    page.on_console()
    page.evaluate("console.log('peca-ok')")
    mensagens = ""
    for _ in range(20):
        mensagens = " ".join(item.get("text", "") for item in page.console_messages())
        if "peca-ok" in mensagens:
            break
        page.wait(100)
    expect("peca-ok" in mensagens, mensagens)
