import requests
from bs4 import BeautifulSoup
from urllib.parse import quote_plus

def scrape_itch_game(nome_jogo):
    busca = quote_plus(nome_jogo)
    url = f"https://itch.io/search?q={busca}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    try:
        resp = requests.get(url, headers=headers, timeout=15)
        soup = BeautifulSoup(resp.text, "html.parser")
        
        celulas = soup.select(".game_cell")
        if not celulas:
            return None
            
        primeiro = celulas[0]
        
        titulo_el = primeiro.select_one(".title a")
        if not titulo_el:
            return None
        nome = titulo_el.text.strip()
        link = titulo_el["href"]
        
        preco_el = primeiro.select_one(".price_value")
        if preco_el:
            preco_atual = preco_el.text.strip()
            preco_original = preco_atual
        else:
            preco_atual = "Grátis"
            preco_original = "Grátis"
            
        img_el = primeiro.select_one(".game_thumb img")
        imagem = None
        if img_el:
            imagem = img_el.get("src") or img_el.get("data-lazy_src")
            
        return {
            "nome": nome,
            "preco_atual": preco_atual,
            "preco_original": preco_original,
            "imagem": imagem,
            "link": link
        }
    except Exception as e:
        return None

if __name__ == "__main__":
    jogo = input("Digite o nome do jogo: ").strip()
    resultado = scrape_itch_game(jogo)
    print(resultado)
