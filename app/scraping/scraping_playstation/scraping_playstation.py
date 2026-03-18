from urllib.parse import quote_plus
from difflib import SequenceMatcher
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
import time


def iniciar_driver():
    options = webdriver.ChromeOptions()
    options.add_argument("--headless=new")
    options.add_argument("--disable-gpu")
    options.add_argument("--no-sandbox")
    options.add_argument("--disable-dev-shm-usage")
    options.add_argument("--lang=pt-BR")
    options.add_argument("--window-size=1600,3000")

    service = Service(ChromeDriverManager().install())
    driver = webdriver.Chrome(service=service, options=options)
    return driver


def normalizar(txt):
    if not txt:
        return ""
    return " ".join(txt.lower().strip().split())


def similaridade(a, b):
    return SequenceMatcher(None, normalizar(a), normalizar(b)).ratio()


def extrair_nome_card(card):
    seletores = [
        "[data-qa*='product-name']",
        "[data-qa*='title']",
        "span",
        "div"
    ]

    for seletor in seletores:
        try:
            elementos = card.find_elements(By.CSS_SELECTOR, seletor)
            for el in elementos:
                txt = el.text.strip()
                if not txt:
                    continue

                low = txt.lower()
                if "r$" in low or "%" in low:
                    continue
                if low in ["ps4", "ps5", "standard edition", "demo", "bundle"]:
                    continue
                if len(txt) < 2:
                    continue

                return txt
        except:
            pass

    texto = card.text.strip()
    if texto:
        linhas = [x.strip() for x in texto.split("\n") if x.strip()]
        for linha in linhas:
            low = linha.lower()
            if "r$" in low or "%" in low:
                continue
            return linha

    return None


def extrair_imagem_card(card):
    try:
        imgs = card.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            src = img.get_attribute("src")
            if src:
                return src
    except:
        pass
    return None


def buscar_melhor_resultado(driver, nome_jogo):
    wait = WebDriverWait(driver, 5)

    url = f"https://store.playstation.com/pt-br/search/{quote_plus(nome_jogo)}"
    driver.get(url)

    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)

    cards = driver.find_elements(By.CSS_SELECTOR, "a[href*='/concept/'], a[href*='/product/']")
    candidatos = []
    vistos = set()

    for card in cards:
        try:
            href = card.get_attribute("href")
            if not href or href in vistos:
                continue
            vistos.add(href)

            nome = extrair_nome_card(card)
            img = extrair_imagem_card(card)

            if not nome:
                continue

            score = similaridade(nome_jogo, nome)

            nome_busca = normalizar(nome_jogo)
            nome_card = normalizar(nome)
            if nome_busca in nome_card:
                score += 0.25

            candidatos.append({
                "nome": nome,
                "link": href,
                "imagem": img,
                "score": score
            })
        except:
            continue

    if not candidatos:
        return None

    candidatos.sort(key=lambda x: x["score"], reverse=True)
    return candidatos[0]


def tentar_texto(driver, seletores):
    for seletor in seletores:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, seletor)
            for el in els:
                txt = el.text.strip()
                if txt:
                    return txt
        except:
            pass
    return None


def extrair_preco_pagina(driver):
    preco_atual = None
    preco_original = None

    seletores_atual = [
        "[data-qa*='mfeCtaMain'] [data-qa*='finalPrice']",
        "[data-qa*='mfeCtaMain'] [data-qa*='offer0#finalPrice']",
        "[data-qa*='mfeCtaMain'] [data-qa*='price']",
        "[data-qa*='finalPrice']",
        "[data-qa*='salePrice']",
        "[data-qa*='discountedPrice']",
        "span[data-qa*='finalPrice']",
        "span[data-qa*='price']"
    ]

    seletores_original = [
        "[data-qa*='mfeCtaMain'] [data-qa*='originalPrice']",
        "[data-qa*='mfeCtaMain'] [data-qa*='strikethroughPrice']",
        "[data-qa*='originalPrice']",
        "[data-qa*='strikethroughPrice']",
        "span[data-qa*='originalPrice']"
    ]

    preco_atual = tentar_texto(driver, seletores_atual)
    preco_original = tentar_texto(driver, seletores_original)

    if not preco_atual:
        try:
            elementos = driver.find_elements(By.XPATH, "//*[contains(text(),'R$')]")
            precos = []
            for el in elementos:
                txt = el.text.strip()
                if txt and txt not in precos and len(txt) <= 30:
                    precos.append(txt)

            if len(precos) >= 1:
                preco_atual = precos[0]
            if len(precos) >= 2:
                preco_original = precos[1]
        except:
            pass

    if preco_atual and not preco_original:
        preco_original = preco_atual

    return preco_atual, preco_original


def extrair_nome_pagina(driver):
    seletores = [
        "h1",
        "[data-qa='mfe-game-title#name']",
        "[data-qa*='title']"
    ]

    for seletor in seletores:
        try:
            els = driver.find_elements(By.CSS_SELECTOR, seletor)
            for el in els:
                txt = el.text.strip()
                if txt:
                    return txt
        except:
            pass
    return None


def extrair_imagem_pagina(driver):
    try:
        imgs = driver.find_elements(By.TAG_NAME, "img")
        for img in imgs:
            src = img.get_attribute("src")
            alt = (img.get_attribute("alt") or "").lower()
            if src and ("playstation" in src or "image" in src or "w=" in src):
                if alt:
                    return src

        for img in imgs:
            src = img.get_attribute("src")
            if src:
                return src
    except:
        pass
    return None


def scrape_playstation_game(nome_jogo):
    driver = iniciar_driver()
    wait = WebDriverWait(driver, 5)

    try:
        melhor = buscar_melhor_resultado(driver, nome_jogo)
        if not melhor:
            return None

        driver.get(melhor["link"])
        wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
        time.sleep(2)

        nome = extrair_nome_pagina(driver) or melhor["nome"]
        imagem = extrair_imagem_pagina(driver) or melhor["imagem"]
        preco_atual, preco_original = extrair_preco_pagina(driver)

        return {
            "plataforma": "PlayStation",
            "nome": nome,
            "preco_atual": preco_atual,
            "preco_original": preco_original,
            "imagem": imagem,
            "link": melhor["link"]
        }

    finally:
        driver.quit()


if __name__ == "__main__":
    jogo = input("Digite o nome do jogo na PlayStation Store: ").strip()
    resultado = scrape_playstation_game(jogo)

    if resultado:
        print("Plataforma:", resultado["plataforma"])
        print("Nome:", resultado["nome"])
        print("Preço atual:", resultado["preco_atual"])
        print("Preço original:", resultado["preco_original"])
        print("Imagem:", resultado["imagem"])
        print("Link:", resultado["link"])
    else:
        print("Nenhum jogo encontrado.")
