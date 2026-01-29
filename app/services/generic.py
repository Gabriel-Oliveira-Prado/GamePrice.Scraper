import requests
from bs4 import BeautifulSoup


def scrape_basic_info(url: str):
    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    response = requests.get(url, headers=headers)
    soup = BeautifulSoup(response.text, "html.parser")

    # 🔹 Título (Steam)
    title_tag = soup.find("div", id="appHubAppName")
    title = title_tag.text.strip() if title_tag else "Não encontrado"

    # 🔹 Preço (Steam)
    price_tag = soup.select_one(".game_purchase_price, .discount_final_price")
    price = price_tag.text.strip() if price_tag else "Indisponível"

    return {
        "title": title,
        "price": price,
        "url": url
    }
