from urllib.parse import quote_plus
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager
import time


def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=pt-BR")
    options.add_argument("--window-size=1400,2200")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def pegar_primeiro_link_jogo(driver, nome_jogo):
    wait = WebDriverWait(driver, 5)

    busca = quote_plus(nome_jogo)
    url = f"https://www.gog.com/en/games?query={busca}"
    driver.get(url)

    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(3)

    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/en/game/']")

    vistos = set()
    candidatos = []

    for link in links:
        try:
            href = link.get_attribute("href")
            if not href or "/en/game/" not in href:
                continue
            if href in vistos:
                continue

            vistos.add(href)

            texto = link.text.strip().lower()
            candidatos.append((href, texto))
        except:
            continue

    nome_lower = nome_jogo.lower()

    for href, texto in candidatos:
        if nome_lower in texto:
            return href

    return candidatos[0][0] if candidatos else None


def extrair_imagem(driver, nome=None):
    try:
        imgs = driver.find_elements(By.TAG_NAME, "img")

        for img in imgs:
            try:
                src = img.get_attribute("src")
                alt = (img.get_attribute("alt") or "").lower()

                if not src:
                    continue

                if (
                    "images.gog-statics.com" in src
                    or "gog-cdn" in src
                    or "menu-product-item" in src
                ):
                    if nome:
                        if nome.lower() in alt or alt == "":
                            return src
                    else:
                        return src
            except:
                continue
    except:
        pass

    return None


def extrair_dados_jogo(driver, url_jogo):
    wait = WebDriverWait(driver, 5)
    driver.get(url_jogo)

    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(3)

    nome = None
    preco_atual = None
    preco_original = None
    imagem = None

    try:
        nome = wait.until(
            EC.presence_of_element_located((By.TAG_NAME, "h1"))
        ).text.strip()
    except:
        nome = None

    imagem = extrair_imagem(driver, nome)

    try:
        preco_atual = wait.until(
            EC.presence_of_element_located(
                (By.CSS_SELECTOR, "span.product-actions-price__final-amount")
            )
        ).text.strip()
    except:
        preco_atual = None

    try:
        preco_original = driver.find_element(
            By.CSS_SELECTOR,
            "span.product-actions-price__base-amount"
        ).text.strip()
    except:
        preco_original = None

    if preco_atual and not preco_original:
        preco_original = preco_atual

    if preco_atual:
        if preco_atual.upper() == "FREE":
            preco_original = "FREE"

    return {
        "plataforma": "GOG",
        "nome": nome,
        "preco_atual": preco_atual,
        "preco_original": preco_original,
        "imagem": imagem,
        "link": url_jogo
    }


def scrape_gog_game(nome_jogo):
    driver = iniciar_driver()

    try:
        link_jogo = pegar_primeiro_link_jogo(driver, nome_jogo)

        if not link_jogo:
            return None

        dados = extrair_dados_jogo(driver, link_jogo)
        return dados

    finally:
        driver.quit()


if __name__ == "__main__":
    jogo = input("Digite o nome do jogo na GOG: ").strip()
    resultado = scrape_gog_game(jogo)

    if resultado:
        print("Plataforma:", resultado["plataforma"])
        print("Nome:", resultado["nome"])
        print("Preço atual:", resultado["preco_atual"])
        print("Preço original:", resultado["preco_original"])
        print("Imagem:", resultado["imagem"])
        print("Link:", resultado["link"])
    else:
        print("Nenhum jogo encontrado.")
