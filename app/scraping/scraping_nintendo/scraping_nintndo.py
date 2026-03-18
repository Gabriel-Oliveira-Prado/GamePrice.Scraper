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
    try:
        texto = card.text.strip()
        if not texto:
            return None

        linhas = [x.strip() for x in texto.split("\n") if x.strip()]

        ignorar = {
            "nintendo switch",
            "nintendo switch 2",
            "versão digital",
            "digital",
            "comprar",
            "loading"
        }

        for linha in linhas:
            low = linha.lower()
            if "r$" in low or "$" in low or "%" in low:
                continue
            if low in ignorar:
                continue
            if len(linha) < 2:
                continue
            return linha
    except:
        pass

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

    url = f"https://www.nintendo.com/pt-br/search/?q={quote_plus(nome_jogo)}"
    driver.get(url)

    wait.until(lambda d: d.execute_script("return document.readyState") == "complete")
    time.sleep(2)

    links = driver.find_elements(By.CSS_SELECTOR, "a[href*='/store/products/']")
    candidatos = []
    vistos = set()

    for link in links:
        try:
            href = link.get_attribute("href")
            if not href or href in vistos:
                continue
            vistos.add(href)

            nome = extrair_nome_card(link)
            imagem = extrair_imagem_card(link)

            if not nome:
                nome = link.get_attribute("aria-label") or None

            if not nome:
                continue

            score = similaridade(nome_jogo, nome)

            nome_busca = normalizar(nome_jogo)
            nome_card = normalizar(nome)

            if nome_busca in nome_card:
                score += 0.25

            palavras = [p for p in nome_busca.split() if len(p) > 2]
            bonus = sum(1 for p in palavras if p in nome_card) * 0.03
            score += bonus

            candidatos.append({
                "nome": nome,
                "link": href,
                "imagem": imagem,
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
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            for el in elementos:
                txt = el.text.strip()
                if txt:
                    return txt
        except:
            pass
    return None


def extrair_nome_pagina(driver):
    seletores = [
        "h1",
        "[data-testid='pdp-product-title']",
        "[class*='ProductHero'] h1",
        "[class*='product'] h1"
    ]

    return tentar_texto(driver, seletores)


def extrair_imagem_pagina(driver):
    try:
        imgs = driver.find_elements(By.TAG_NAME, "img")

        for img in imgs:
            try:
                src = img.get_attribute("src")
                alt = (img.get_attribute("alt") or "").lower()

                if not src:
                    continue

                if "nintendo.com" in src or "images" in src or "cloudinary" in src:
                    if alt:
                        return src
            except:
                continue

        for img in imgs:
            src = img.get_attribute("src")
            if src:
                return src
    except:
        pass

    return None


def extrair_precos_pagina(driver):
    preco_atual = None
    preco_original = None

    seletores_atual = [
        "[data-testid='formatted-value']",
        "[class*='price']",
        "[class*='Price']",
        "span[class*='price']",
        "div[class*='price']"
    ]

    seletores_original = [
        "[class*='strike']",
        "[class*='original']",
        "[class*='base']",
        "span[class*='strike']",
        "span[class*='original']"
    ]

    for seletor in seletores_atual:
        try:
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            for el in elementos:
                txt = el.text.strip()
                low = txt.lower()

                if not txt:
                    continue

                if "r$" in low or "$" in low or low == "grátis" or low == "free":
                    preco_atual = txt
                    break
            if preco_atual:
                break
        except:
            pass

    for seletor in seletores_original:
        try:
            elementos = driver.find_elements(By.CSS_SELECTOR, seletor)
            for el in elementos:
                txt = el.text.strip()
                low = txt.lower()

                if not txt:
                    continue

                if "r$" in low or "$" in low:
                    preco_original = txt
                    break
            if preco_original:
                break
        except:
            pass

    if not preco_atual:
        try:
            elementos = driver.find_elements(By.XPATH, "//*[contains(text(),'R$') or contains(text(),'$') or contains(text(),'Grátis') or contains(text(),'FREE')]")
            precos = []

            for el in elementos:
                txt = el.text.strip()
                if txt and txt not in precos and len(txt) <= 40:
                    precos.append(txt)

            if len(precos) >= 1:
                preco_atual = precos[0]
            if len(precos) >= 2:
                preco_original = precos[1]
        except:
            pass

    if preco_atual and not preco_original:
        preco_original = preco_atual

    if preco_atual and preco_atual.lower() in ["grátis", "free"]:
        preco_original = preco_atual

    return preco_atual, preco_original


def scrape_nintendo_game(nome_jogo):
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
        preco_atual, preco_original = extrair_precos_pagina(driver)

        return {
            "plataforma": "Nintendo",
            "nome": nome,
            "preco_atual": preco_atual,
            "preco_original": preco_original,
            "imagem": imagem,
            "link": melhor["link"]
        }

    finally:
        driver.quit()


if __name__ == "__main__":
    jogo = input("Digite o nome do jogo na Nintendo: ").strip()
    resultado = scrape_nintendo_game(jogo)

    if resultado:
        print("Plataforma:", resultado["plataforma"])
        print("Nome:", resultado["nome"])
        print("Preço atual:", resultado["preco_atual"])
        print("Preço original:", resultado["preco_original"])
        print("Imagem:", resultado["imagem"])
        print("Link:", resultado["link"])
    else:
        print("Nenhum jogo encontrado.")
