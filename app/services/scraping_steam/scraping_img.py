# scraping_img.py
import re
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def extrair_appid(url):
    m = re.search(r"/app/(\d+)", url)
    return m.group(1) if m else None

def pegar_imagem_jogo(termo, pais="br", idioma="brazilian"):
    search_url = "https://store.steampowered.com/search/"
    params = {
        "term": termo,
        "category1": 998,
        "cc": pais,
        "l": idioma,
    }

    resp = requests.get(search_url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    soup = BeautifulSoup(resp.text, "html.parser")
    termo_normalizado = termo.lower().strip()

    for row in soup.select("a.search_result_row"):
        titulo_el = row.select_one("span.title")
        if not titulo_el:
            continue

        nome = titulo_el.get_text(strip=True)
        if nome.lower() != termo_normalizado:
            continue

        url_jogo = row.get("href")
        appid = extrair_appid(url_jogo)
        if not appid:
            return None

        return f"https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/{appid}/capsule_616x353.jpg"

    return None


if __name__ == "__main__":
    termo = input("Nome do jogo: ")
    print(pegar_imagem_jogo(termo))
