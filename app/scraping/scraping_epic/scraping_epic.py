from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from selenium.webdriver.chrome.service import Service


def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--start-maximized")
    options.add_argument("--lang=pt-BR")
    options.add_argument("--disable-blink-features=AutomationControlled")
    options.add_experimental_option("excludeSwitches", ["enable-automation"])
    options.add_experimental_option("useAutomationExtension", False)

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    driver.execute_script(
        "Object.defineProperty(navigator, 'webdriver', {get: () => undefined})"
    )
    return driver


def extrair_precos(texto_card):
    linhas = [l.strip() for l in texto_card.split("\n") if l.strip()]

    preco_atual = None
    preco_original = None

    precos = []
    for linha in linhas:
        normalizada = linha.replace("\xa0", " ").strip()
        if "R$" in normalizada or "BRL" in normalizada or normalizada.lower() == "grátis" or normalizada.lower() == "free":
            precos.append(normalizada)

    if len(precos) >= 2:
        preco_original = precos[0]
        preco_atual = precos[1]
    elif len(precos) == 1:
        preco_atual = precos[0]

    return preco_atual, preco_original


def scrape_epic_game(nome_jogo):
    driver = iniciar_driver()
    wait = WebDriverWait(driver, 5)

    try:
        busca = quote_plus(nome_jogo)
        url = f"https://store.epicgames.com/pt-BR/browse?q={busca}&sortBy=relevancy&sortDir=DESC&count=40"
        driver.get(url)

        wait.until(
            EC.presence_of_all_elements_located((By.CSS_SELECTOR, "a[href*='/p/']"))
        )

        cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/p/']")
        resultados = []
        vistos = set()

        for card in cards:
            try:
                link = card.get_attribute("href")
                if not link or link in vistos:
                    continue
                vistos.add(link)

                texto = card.text.strip()
                if not texto:
                    continue

                nome = None
                preco_atual = None
                preco_original = None
                imagem = None

                linhas = [l.strip() for l in texto.split("\n") if l.strip()]

                preco_atual, preco_original = extrair_precos(texto)

                for i, linha in enumerate(linhas):
                    linha_lower = linha.lower()
                    if (
                        "r$" in linha_lower
                        or "brl" in linha_lower
                        or linha_lower == "grátis"
                        or linha_lower == "free"
                    ):
                        if i > 0:
                            nome = linhas[i - 1]
                        break

                if not nome and len(linhas) >= 2:
                    nome = linhas[1]
                elif not nome and linhas:
                    nome = linhas[0]

                try:
                    img_el = card.find_element(By.TAG_NAME, "img")
                    imagem = img_el.get_attribute("src")
                    if not imagem:
                        imagem = img_el.get_attribute("data-src")
                except:
                    imagem = None

                resultados.append({
                    "plataforma": "Epic Games",
                    "nome": nome,
                    "preco_atual": preco_atual,
                    "preco_original": preco_original,
                    "imagem": imagem,
                    "link": link
                })

            except:
                continue

        correspondencias = []
        for item in resultados:
            nome_item = (item["nome"] or "").lower()
            if nome_jogo.lower() in nome_item:
                correspondencias.append(item)

        if correspondencias:
            return correspondencias[0]

        return resultados[0] if resultados else None

    finally:
        driver.quit()


if __name__ == "__main__":
    jogo = input("Digite o nome do jogo: ").strip()
    resultado = scrape_epic_game(jogo)

    if resultado:
        print("Plataforma:", resultado["plataforma"])
        print("Nome:", resultado["nome"])
        print("Preço atual:", resultado["preco_atual"])
        print("Preço sem promoção:", resultado["preco_original"])
        print("Imagem:", resultado["imagem"])
        print("Link:", resultado["link"])
    else:
        print("Nenhum jogo encontrado.")