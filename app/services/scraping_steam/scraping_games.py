# scraping_games.py
import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": (
        "Mozilla/5.0 (Windows NT 10.0; Win64; x64) "
        "AppleWebKit/537.36 (KHTML, like Gecko) "
        "Chrome/120.0.0.0 Safari/537.36"
    )
}

def buscar_jogo_exato(termo, pais="br", idioma="brazilian"):
    url = "https://store.steampowered.com/search/"
    params = {
        "term": termo,
        "category1": 998,
        "cc": pais,
        "l": idioma,
    }

    resp = requests.get(url, params=params, headers=HEADERS, timeout=15)
    resp.raise_for_status()

    from bs4 import BeautifulSoup
    soup = BeautifulSoup(resp.text, "html.parser")

    termo_normalizado = termo.strip().lower()

    for row in soup.select("a.search_result_row"):
        titulo_el = row.select_one("span.title")
        nome = titulo_el.get_text(strip=True) if titulo_el else None
        if not nome:
            continue

        if nome.lower() != termo_normalizado:
            continue

        preco_original = "Não disponível"
        preco_atual = "Não disponível"

        original_el = row.select_one(".discount_original_price")
        final_el = row.select_one(".discount_final_price")

        if final_el:
            preco_atual = final_el.get_text(strip=True)
        if original_el:
            preco_original = original_el.get_text(strip=True)

        if not final_el:
            price_el = row.select_one("div.search_price")
            if price_el:
                texto = price_el.get_text(" ", strip=True)

                if ("gratuito" in texto.lower()) or ("free" in texto.lower()):
                    preco_atual = "Gratuito para jogar"
                    preco_original = preco_atual
                elif "R$" in texto:
                    partes = texto.split("R$")
                    partes = [p.strip() for p in partes if p.strip()]
                    if partes:
                        preco_atual = "R$ " + partes[-1]
                        preco_original = preco_atual
                else:
                    preco_atual = texto
                    preco_original = texto

        url_jogo = row.get("href")

        return {
            "nome": nome,
            "preco_original": preco_original,
            "preco_atual": preco_atual,
            "url": url_jogo,
        }

    return None


if __name__ == "__main__":
    termo = input("Nome do jogo: ")
    print(buscar_jogo_exato(termo))
