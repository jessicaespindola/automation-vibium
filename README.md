# Peças & Prova

Laboratório de automação com o [Vibium](https://vibium.com/), de Jason Huggins (Selenium, Appium). A frase do site oficial é **“Agents make it. We check it.”**: o agente constrói, o Vibium confere no navegador e guarda a evidência.

Este repositório tem dois alvos.

1. **Páginas locais** em `fixtures/`. Formulário, diálogo, frame, shadow DOM, upload, download, arraste, ponteiro, mídia, geolocalização e relógio. Servem para aprender a superfície da ferramenta sem depender de um site de terceiros.
2. **A loja de demonstração deles**, [var.parts](https://var.parts). O checkout da vitrine segue o tutorial oficial de gravação: escolher o Vibium Battery Pack, ir ao carrinho e avançar até o pagamento.

A suíte local afirma o que dá para afirmar em código. Run e Check, a parte em que um modelo age e outro modelo julga, ficam num comando separado porque pedem provedor de IA.

## O que é o Vibium

Um binário de cerca de 10 MB sobe o Chrome sozinho, fala **WebDriver BiDi** (protocolo aberto, sem amarrar o controle ao DevTools proprietário) e expõe a mesma sessão de três jeitos: CLI, servidor MCP e bibliotecas em JavaScript/TypeScript, Python e Java. A licença é Apache 2.0. Windows x64 é suportado. Chrome é o padrão; Firefox também funciona. A faixa de vídeo da gravação exige Firefox 154 ou mais novo.

O vídeo que viralizou em 2025 era o pitch do Jason para o batch F25 da Y Combinator, não um lançamento formal. A YC recusou. O produto aberto que existe hoje é o repositório abaixo. A versão publicada nos registros quando este laboratório foi escrito é a **26.8.21**. Confira a tag atual no GitHub antes de travar uma versão em produção.

| O quê | Onde |
|---|---|
| Site | [vibium.com](https://vibium.com/) |
| Código e docs | [github.com/VibiumDev/vibium](https://github.com/VibiumDev/vibium) |
| npm | [npmjs.com/package/vibium](https://www.npmjs.com/package/vibium) — autor `Jason Huggins <hugs@vibium.com>` |
| PyPI | [pypi.org/project/vibium](https://pypi.org/project/vibium/) |
| Maven | `com.vibium:vibium` |
| Primeiros passos | [JavaScript](https://github.com/VibiumDev/vibium/blob/main/docs/tutorials/getting-started-js.md), [Python](https://github.com/VibiumDev/vibium/blob/main/docs/tutorials/getting-started-python.md), [Java](https://github.com/VibiumDev/vibium/blob/main/docs/tutorials/getting-started-java.md) |
| Referência da CLI | [skills/browser/SKILL.md](https://github.com/VibiumDev/vibium/blob/main/skills/browser/SKILL.md) |
| Referência da API | [docs/reference/api.md](https://github.com/VibiumDev/vibium/blob/main/docs/reference/api.md) |
| Seletores | [docs/reference/selectors.md](https://github.com/VibiumDev/vibium/blob/main/docs/reference/selectors.md) |
| Run e Check | [Introducing Run and Check](https://github.com/VibiumDev/vibium/blob/main/docs/updates/2026-09-07-run-and-check.md) |
| Player das gravações | [player.vibium.dev](https://player.vibium.dev) |
| GitHub do Jason | [github.com/hugs](https://github.com/hugs/) |

A documentação oficial pede **Python 3.11+**. O tutorial de instalação também cobre o cache do Chrome for Testing: no Windows, `%LOCALAPPDATA%\vibium\`.

## Por que ele não é “mais um Selenium”

O fluxo que um agente deve aprender primeiro não começa em seletor CSS. A CLI mapeia a página, devolve referências `@e1`, `@e2`, age nelas e mostra o que mudou:

```bash
vibium go https://var.parts
vibium map
vibium click @e1
vibium diff map
vibium find text "Sign In"
```

Esse `vibium` é o binário completo, não o atalho que o pip 26.8.21 coloca no PATH. A seção Instalar mostra como achar o executável.

`map` e `diff map` existem na CLI e no MCP. Não existem no client Python. Por isso o laboratório `mapa` chama o binário, e o resto da suíte usa a API Python.

No client Python 26.8.21, o primeiro argumento de `find` é um seletor CSS. Se ele vier preenchido, `text`, `label`, `role` e os outros critérios semânticos são ignorados. `page.find("a", text="Loja")` devolve o primeiro `<a>`. O jeito que combina é omitir o CSS: `page.find(text="Loja")` ou `page.find(role="button", text="Salvar")`.

`find(label=...)` acha o controle pelo `<label for>`. Label só embrulhando o input, sem `for`/`id`, não foi encontrado nesta versão. Os formulários do laboratório usam os dois ligados.

A outra diferença é a separação entre agir e julgar.

| | O que faz | Veredito |
|---|---|---|
| **Run** | Cumpre um objetivo em linguagem natural, na sessão aberta | `completed` ou `not_completed` |
| **Check** | Julga uma afirmação com outro contexto de modelo, ao vivo ou lendo um zip já salvo (também lê trace do Playwright) | `passed`, `failed` ou `inconclusive` |

Check não herda a conversa de quem construiu nem a de Run. O julgamento do modelo descreve a evidência; não substitui asserção determinística. A documentação oficial diz isso com todas as letras. O pacote **26.8.21** ainda não inclui Run nem esse Check: no binário dessa versão, `check` marca um checkbox. O desenho abaixo é o que está em `main`.

```bash
vibium run "open https://var.parts and add one battery pack to the cart" --keep-open
vibium check "the cart contains exactly one battery pack" -o cart-check.zip
vibium check "the cart contained exactly one battery pack" -i cart-check.zip
vibium stop
```

`-o` grava. `-i` lê uma gravação já feita, com o browser fechado. `--report` escreve o veredito em JSON.

Na API Python, o browser conectado é chamável: `vibe("abra a página")` é o mesmo que `vibe.run(...)`. `vibe.check("a frase")` julga a sessão. `browser.check("a frase", record="arquivo.zip")` julga um zip sem abrir o browser.

Run e Check pedem modelo. `vibium setup` grava o molde em `~/.config/vibium/ai.env` (no Windows o equivalente fica sob o perfil do usuário; `vibium config init` gera o template). A credencial fica na variável nativa do provedor, por exemplo `OPENAI_API_KEY`. Comandos diretos (`go`, `find`, `click`, a suíte deste repositório) não precisam disso. Confira com `vibium ready`, `vibium ready browser` e `vibium ready ai`.

## Arquitetura

```
LLM / agente (Cursor, Claude Code, Codex, Gemini)
        | CLI                         | MCP (stdio)
        v                             v
binário Vibium (~10 MB)
  CLI + servidor MCP
  proxy WebDriver BiDi  <-------->  Chrome ou Firefox
        ^
        | WebSocket BiDi
clients JS/TS, Python e Java (async e sync)
```

### O que acontece em `python -m pecas_e_prova suite`

O Python não dirige o Chrome. `browser.start()` sobe o `vibium.exe`, e esse binário abre o **Chrome for Testing** e fica no meio, falando WebDriver BiDi por WebSocket. Cada `go`, `find`, `click` e `fill` é uma mensagem nessa conexão, não uma requisição HTTP nova como no WebDriver antigo. O clique aparece quase junto com o `ok` no terminal.

```
python -m pecas_e_prova suite
        |
        +-- servidor local (fixtures/ em 127.0.0.1, porta livre)
        |
        +-- browser.start()
              |
              vibium.exe  (~10 MB, Go: proxy BiDi)
                    |
                    Chrome for Testing  (uma janela, uma aba)
                          |
                          as páginas da oficina: loja, formulário, diálogo…
```

As páginas não vêm da internet. A suíte sobe um servidor só com os arquivos de `fixtures/`. O endereço impresso, por exemplo `http://127.0.0.1:62995`, é essa oficina local. Sem rede, sem login, sem espera de site.

Uma sessão só. `bro.page()` pega a única aba e a suíte a traz para a frente uma vez (`bring_to_front` e `set_window`). Entre um laboratório e o outro ela limpa cookie e storage nessa mesma página e, no modo visível, espera 700 ms para o clique dar para ver. São nove roteiros curtos em sequência. No fim, `bro.stop()` derruba o Chrome e o proxy.

O agente (CLI ou MCP) entra nesse mesmo binário. Aqui quem confere é o Python: descreve o passo e afirma o resultado. O Chrome só executa.

Dois detalhes existem porque a página é compartilhada. O relógio falso é instalado e, no fim do laboratório, retomado com `clock.resume()`, para os labs seguintes não ficarem presos no tempo falso. O isolamento de dois contextos (`new_context()`) só roda com `--headless`: no modo visível um contexto novo é outra janela, e a suíte fica em uma.

Skills oficiais, instaláveis com `npx skills add https://github.com/VibiumDev/vibium` ou `vibium add-skill`:

- **browser** — explorar, agir, gravar e cumprir um objetivo em linguagem natural.
- **check** — avaliar se uma afirmação se sustenta no browser ou numa gravação.

No Cursor, o atalho de MCP publicado no README deles é da família `npx -y vibium mcp`. O guia está em [getting-started-mcp.md](https://github.com/VibiumDev/vibium/blob/main/docs/tutorials/getting-started-mcp.md).

## Ver no ar

Há duas coisas diferentes. As **páginas** ficam no ar para você clicar. A **automação** abre outro Chrome, executa os passos e fecha.

Na raiz do repositório, com o ambiente já instalado (`pip install -r requirements.txt` e `vibium install`):

```powershell
python -m pecas_e_prova ver
```

Isso sobe as páginas em [http://127.0.0.1:8765](http://127.0.0.1:8765) e abre o navegador. O terminal fica ocupado de propósito. Ctrl+C derruba o site.

Para ver o Chrome do Vibium executar a suíte na sua frente:

```powershell
python -m pecas_e_prova suite
```

Abre **uma** janela, Chrome for Testing, e os cliques acontecem nela. Ela costuma nascer atrás do editor: traga-a para a frente. Fecha sozinha no fim. `--headless` esconde a janela e aí não há clique para ver.

## Instalar e rodar

No PowerShell, na raiz deste repositório:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install -r requirements.txt
vibium install
```

`pip install` traz o client Python e o binário. `vibium install` baixa o Chrome for Testing antes do primeiro teste. Se pular esse passo, o Chrome baixa na primeira chamada a `browser.start()`.

Na versão 26.8.21, o `vibium` que o pip coloca no PATH só aceita `install` e `version`. `go`, `map`, `record`, `mcp` e os outros comandos estão no binário que o client usa por baixo. O laboratório `mapa` resolve esse caminho com `vibium.binary.find_vibium_bin()`. Para chamar a CLI completa no PowerShell:

```powershell
$vibium = python -c "from vibium.binary import find_vibium_bin; print(find_vibium_bin())"
& $vibium map
```

Nos exemplos mais abaixo, `vibium` quer dizer esse executável.

A janela abre de propósito. Para esconder:

```powershell
python -m pecas_e_prova --headless
```

| Comando | O que exercita | Precisa de modelo? | Precisa de rede externa? |
|---|---|---|---|
| `python -m pecas_e_prova ver` | Deixa as páginas no ar em http://127.0.0.1:8765 | não | não |
| `python -m pecas_e_prova` | Suíte local, nove laboratórios, um contexto limpo cada | não | não |
| `python -m pecas_e_prova mapa` | CLI: `go`, `map`, `find`, `click @ref`, `diff map` | não | não |
| `python -m pecas_e_prova vitrine` | Checkout oficial em var.parts, com gravação | não | sim |
| `python -m pecas_e_prova agente` | Explica Run e Check. No 26.8.21 só imprime a receita, porque o client ainda não tem `Browser.run` | não neste pacote | não |
| `python -m pecas_e_prova video` | O mesmo carrinho local, com faixa WebM | não | não, mas exige Firefox 154+ |

Artefatos (screenshot, PDF, zip, estado) caem em `evidence/`, que não entra no git. Abra qualquer `*.zip` em [player.vibium.dev](https://player.vibium.dev): timeline, screenshots, rede, DOM e, no Firefox, o vídeo.

O Vibium **26.8.21** não emite um relatório das várias passagens da suíte. O que ele guarda é a evidência de um fluxo gravado: o zip do laboratório 09 (`evidence/loja.zip`), sobrescrito a cada execução, mais screenshot, PDF e `estado.json` dos laboratórios que escrevem arquivo. Na documentação de `main`, `vibium check --report` grava o veredito JSON de **um** Check. Esse comando não existe neste pacote, e não é um histórico de dez corridas. A saída abaixo foi medida pelo Python, com `PECAS_HEADLESS=1`, e o log cru de cada passagem ficou em `evidence/run-01.txt` … `evidence/run-10.txt` (também fora do git).

### Dez passagens headless

Em 5 de novembro de 2026, no Chrome for Testing 157 com o Vibium 26.8.21, a suíte inteira rodou dez vezes seguidas, headless, na ordem dos nove roteiros. **10/10** saíram com exit 0 e **9/9** laboratórios ok. Nenhuma passagem falhou.

| Passagem | Tempo | Resultado |
|---|---:|---|
| 01 | 74,0 s | 9/9 |
| 02 | 73,2 s | 9/9 |
| 03 | 74,0 s | 9/9 |
| 04 | 74,0 s | 9/9 |
| 05 | 73,4 s | 9/9 |
| 06 | 73,6 s | 9/9 |
| 07 | 71,9 s | 9/9 |
| 08 | 71,4 s | 9/9 |
| 09 | 71,5 s | 9/9 |
| 10 | 73,3 s | 9/9 |

Mínimo 71,4 s, máximo 74,0 s, média 73,0 s, desvio 1,0 s, amplitude 2,6 s. Em toda passagem o laboratório de emulação avisou a mesma coisa: `prefers-color-scheme` continuou `light`, e a geolocalização voltou `erro User denied Geolocation`. O aviso é estável; a suíte segue e conta o laboratório como ok.

O `mapa` usa a sessão de daemon `VIBIUM_SESSION=pecas-mapa` e encerra o daemon no final, para não brigar com o browser que a suíte Python abre.

## O que cada laboratório prova

A barra do site tem sete entradas, não uma aba por arquivo. Hello, sessão e gravação reusam páginas que já existem. Frame, sombra, upload, download, arraste, ponteiro e a geolocalização continuam no roteiro e saíram da barra.

| Etapa | Arquivo | Capacidade oficial |
|---|---|---|
| 01 hello | `pecas_e_prova/labs/hello.py` | `go`, `title`, `screenshot`, `find`, `click`, `wait_for_url` |
| 02 formulário | `labs/formulario.py` | `label`, `placeholder`, `fill`, `type`, `select_option`, `check`/`uncheck` idempotentes, `value`. Salvar vazio mostra um erro por campo; e-mail sem `@` mostra «E-mail inválido.»; a ficha válida mostra «Ficha salva.» e o recibo com e-mail, país e sim. Se o client 26.8.21 responder `SyntaxError: Identifier 'role' has already been declared`, o clique só ocorre quando o estado ainda não é o desejado. O estado é lido com `evaluate` porque `is_checked()` tem o mesmo defeito. Na CLI desta versão: `check`, `uncheck`, `is checked` |
| 03 leitura | `labs/leitura.py` | `text`, `evaluate`, `a11y_tree`, `alt`, screenshot de página inteira, `pdf`, `on_console`. Nesta versão a árvore traz o nome do documento e o `alt` da imagem; o nome do botão vem do `find(role=, text=)`, não do nó da árvore |
| 04 espera | `labs/espera.py` | `wait_for_function`, `is_enabled`, `highlight` |
| 05 sessão | `labs/sessao.py` | cookies, `localStorage`, `storage()`. Com `--headless`, dois `new_context()` que não compartilham estado. No modo visível esse par não abre, para a suíte continuar em uma janela |
| 06 emulação | `labs/emulacao.py` | `set_viewport` (isso muda de fato), `emulate_media` e `set_geolocation`. No Chrome 157 headless o `matchMedia` continuou `light` e a página recebeu “User denied Geolocation”. O laboratório avisa e segue; não trata esse aviso como sucesso do override |
| 07 bordas | `labs/bordas.py` | `on_dialog` antes do clique, frame, seletor `>>` de shadow DOM, `set_files`, leitura do arquivo de download, `drag_to`, `mouse.click` por coordenada, `touch.tap`, `keyboard`. `capture.dialog(lambda: elemento.click())` trava. `capture.download().path()` neste Chrome headless não recebeu a conclusão do download em 120s |
| 08 relógio | `labs/relogio.py` | `clock.install` e `fast_forward`, sem esperar os 5 segundos reais. `clock.resume()` no fim, porque a aba é a mesma dos labs seguintes |
| 09 gravação | `labs/gravacao.py` | `recording.start`, `start_group`, `stop`, zip em `evidence/loja.zip` |
| mapa | `pecas_e_prova/mapa.py` | o hábito `@ref`: mapear, agir, ver o diff. Refs morrem quando a página muda |
| vitrine | `pecas_e_prova/vitrine.py` | o checkout publicado no tutorial deles, contra var.parts |
| agente | `pecas_e_prova/agente.py` | Explica Run e Check. No pacote 26.8.21 o client ainda não tem `Browser.run`, então o comando só descreve a receita de `main` |
| vídeo | `pecas_e_prova/video.py` | `firefox.start()` e `recording.start(video=True)` |

`video=True` no Chrome falha com erro explicativo. A suíte e a vitrine passam `video=False`. Sem o argumento, o Vibium grava vídeo quando o motor sabe e segue sem ele quando não sabe; o retorno de `stop()` traz `video_unavailable` com o motivo.

## Referência curta da CLI

Lista conferida no binário da 26.8.21. `vibium`, aqui, é esse executável — o atalho do pip não encaminha esses comandos; a seção Instalar mostra como obter o caminho. Na documentação de `main`, `check` / `uncheck` já aparecem como `set` / `unset`, e `is checked` como `is set`. A lista com flags novas está na [skill browser](https://github.com/VibiumDev/vibium/blob/main/skills/browser/SKILL.md).

```bash
vibium go https://var.parts
vibium back
vibium forward
vibium reload
vibium url
vibium title

vibium map
vibium map --selector "form"
vibium diff map

vibium find text "Sign In"
vibium find label "Email"
vibium find placeholder "Search"
vibium find role button --name "Add to Cart"
vibium find testid "submit-btn"
vibium find alt "Logo"
vibium find title "Settings"
vibium find xpath "//a[@href='/about']"

vibium click @e1
vibium dblclick @e1
vibium fill @e2 "hello@example.com"
vibium type @e2 " e o resto"
vibium select @e3 "Brasil"
vibium check @e4
vibium uncheck @e4
vibium press Enter
vibium keys "Control+a"
vibium hover @e1
vibium scroll into-view @e1
vibium drag @e1 @e2

vibium text
vibium html
vibium eval "document.title"
vibium screenshot -o page.png
vibium screenshot --annotate -o anotado.png
vibium screenshot --full-page -o pagina.png
vibium pdf -o page.pdf
vibium a11y-tree

vibium wait ".modal"
vibium wait url "/dashboard"
vibium wait text "Success"
vibium wait load
vibium wait fn "window.appReady === true"

vibium is visible @e1
vibium is enabled @e1
vibium is checked @e4
vibium value @e2
vibium attr @e1 href

vibium record start -o evidence/sessao.zip
vibium record group start "escolher peca"
vibium record group stop
vibium record stop

vibium dialog accept
vibium dialog dismiss
vibium upload @e1 caminho\arquivo.txt
vibium frames
vibium frame painel

vibium viewport 390 844
vibium media --color-scheme dark --reduced-motion reduce
vibium geolocation -23.55 -46.63 --accuracy 10

vibium cookies
vibium storage -o evidence/estado.json
vibium storage restore evidence/estado.json

vibium page new --isolated https://exemplo
vibium --session comprador go https://exemplo
vibium daemon stop
vibium stop
```

No client Python os mesmos atos são métodos, em `snake_case`: `page.find(label="E-mail")`, `elemento.fill(...)`, `elemento.set()`, `page.wait_for_url(...)`, `page.context.recording.start(path=...)`. Seletores CSS continuam válidos. `my-card >> #miolo` atravessa um shadow root aberto; `>>>` atravessa qualquer profundidade. Shadow fechado não é alcançável.

Clique, preenchimento e ações parecidas já esperam o elemento ficar acionável. Use espera explícita quando o sinal é a URL, um texto ou uma expressão JavaScript. `sleep` existe e é o último recurso (no máximo 30 segundos na CLI).

## Run e Check

Isso é o que o repositório **main** do Vibium documenta: Run cumpre um objetivo, Check julga uma frase com outro contexto de modelo. O pacote publicado **26.8.21**, que este laboratório instala, ainda não traz `run`, `check` (o de veredito), nem `ready`. No binário dessa versão, `check` marca um checkbox. O comando `agente` explica a diferença e não chama um modelo que o pacote não tem.

Quando essa superfície chegar no pacote, a receita prevista pela documentação é:

Sem modelo, o comando só imprime a receita:

```powershell
python -m pecas_e_prova agente
```

Para executar, exporte o provedor na mesma sessão do shell e ligue a flag. Não commite chave.

```powershell
$env:VIBIUM_AI_PROVIDER = "openai"
$env:VIBIUM_AI_MODEL = "gpt-5.6-sol"
$env:VIBIUM_AI_REASONING_EFFORT = "none"
# OPENAI_API_KEY (ou a variável nativa do provedor escolhido) precisa existir
vibium ready ai
$env:PECAS_RUN_CHECK = "1"
python -m pecas_e_prova agente
```

O script pede ao modelo para adicionar um Battery Pack Local e, em seguida, pede a outro contexto que confirme a frase “exatamente um”. Se `evidence/loja.zip` já existir (a suíte grava esse arquivo), também roda Check sobre o zip, com o browser da gravação já fechado.

Provedores, override por chamada e o que não vai para o log estão em [model providers](https://github.com/VibiumDev/vibium/blob/main/docs/reference/model-providers.md).

## Gravação

O zip segue o formato de trace (timeline, rede, screenshots, snapshots de DOM). Grupos (`start_group` / `stop_group`) aparecem como faixas nomeadas no player. Caminho explícito sobrescreve; sem caminho, o Vibium gera `nome-AAAAMMDD-HHMMSS.zip` para não apagar a tomada anterior.

```powershell
python -m pecas_e_prova
python -m pecas_e_prova vitrine
```

O primeiro escreve `evidence/loja.zip`. O segundo escreve `evidence/var-parts.zip`, o texto da página e um screenshot. Solte o zip em [player.vibium.dev](https://player.vibium.dev).

Vídeo, só no Firefox 154+:

```powershell
python -m pecas_e_prova video
```

O WebM fica dentro de `evidence/video.zip`, ao lado do trace. A câmera filma o contexto que estava ativo no `start` e não segue troca de aba. Conexão remota grava as outras faixas e, por padrão, não a de vídeo.

## O que ainda fica de propósito fora da suíte

Estas superfícies estão na API e na CLI, e a documentação oficial é o lugar certo para elas. Não entram na suíte porque pedem rede, um segundo motor, um modelo ou um aparelho:

- **Run e Check** — comando `agente`, com provedor.
- **Vídeo** — comando `video`, com Firefox.
- **Browser remoto** — `browser.start("ws://host:9515/session")` ou um endpoint WebDriver clássico. Tutorial: [remote-browser.md](https://github.com/VibiumDev/vibium/blob/main/docs/tutorials/remote-browser.md).
- **BiDi cru** — [webdriver-bidi-raw.md](https://github.com/VibiumDev/vibium/blob/main/docs/tutorials/webdriver-bidi-raw.md).
- **Interceptação de rede** — `page.route`, `route.fulfill`, `route.continue_`, `route.abort`, `page.capture.request` e `page.capture.response`.
- **Toque longo e swipe** — `touch.long_press` e `touch.swipe`. A suíte só dá um `tap`. A CLI documenta isso para telefone (Roadie, por exemplo): `vibium swipe`, `vibium long-press`.
- **MCP no Cursor** — subir `vibium mcp` e deixar o agente da IDE dirigir a mesma sessão.

## Layout

```
fixtures/                 páginas e arquivos de treino
pecas_e_prova/
  labs/                   um arquivo por capacidade, usados pela suíte
  suite.py                uma janela, uma aba, nove laboratórios
  mapa.py                 CLI go / map / @ref / diff
  vitrine.py              checkout em var.parts
  agente.py               Run e Check
  video.py                Firefox com faixa de vídeo
evidence/                 gerado na execução, fora do git
```

A suíte reutiliza `bro.page()`. Entre etapas, `clear_cookies()` e `clear_storage()` limpam o estado nessa mesma aba. O par extra de contextos, que prova isolamento, só roda com `--headless`.
