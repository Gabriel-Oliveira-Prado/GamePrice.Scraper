import requests
from bs4 import BeautifulSoup

def scrape_basic_info(url: str) -> dict:
    try:
        resp = requests.get(url, headers={"User-Agent": "Mozilla/5.0"})
        if resp.status_code != 200:
            return None

        soup = BeautifulSoup(resp.text, "html.parser")

        # Steam: título e preço
        title_tag = soup.select_one(".apphub_AppName")
        price_tag = soup.select_one(".game_purchase_price, .discount_final_price")

        title = title_tag.text.strip() if title_tag else "Não encontrado"
        price = price_tag.text.strip() if price_tag else "R$ 0,00"

        return {"title": title, "price": price, "url": url}
    except Exception as e:
        print("Erro ao fazer scrape:", e)
        return None
