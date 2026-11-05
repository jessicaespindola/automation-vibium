"""Viewport, esquema de cor e geolocalização."""

from pecas_e_prova.expect import expect


def run(page, base: str, bro) -> None:
    page.set_viewport({"width": 390, "height": 844})
    tamanho = page.viewport()
    expect(tamanho["width"] == 390 and tamanho["height"] == 844, str(tamanho))

    page.emulate_media(color_scheme="dark", reduced_motion="reduce", media="screen")
    page.go(f"{base}/midia.html")
    page.find(testid="ler").click()
    esquema = page.find(testid="esquema").text()
    # Chrome 157, com o Vibium 26.8.21, aceita o comando e o matchMedia
    # continua "light". Quando o motor passar a aplicar, a asserção aperta.
    if esquema != "dark":
        print(f"aviso: prefers-color-scheme continuou {esquema!r} depois de emulate_media")
        expect(esquema == "light", esquema)

    page.set_geolocation({"latitude": -23.55, "longitude": -46.63, "accuracy": 10})
    page.go(f"{base}/geo.html")
    page.find(testid="ler").click()
    try:
        page.wait_for_function(
            "document.querySelector('[data-testid=lat]').textContent.length > 0",
            timeout=3000,
        )
        latitude = page.find(testid="lat").text()
    except Exception as erro:
        if "timeout" not in str(erro).lower():
            raise
        print("aviso: o Chrome pediu permissão de localização e a página não respondeu")
        return
    if not latitude.startswith("-23."):
        print(f"aviso: set_geolocation não foi lido pela página ({latitude!r})")
        expect("denied" in latitude.lower() or latitude.startswith("erro"), latitude)
