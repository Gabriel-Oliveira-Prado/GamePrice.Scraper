from fastapi import FastAPI, HTTPException
import uvicorn
import sys
import os

sys.path.append(os.path.join(os.path.dirname(__file__), "..", "scraping"))
from scraping_full import buscar_em_todas_lojas

app = FastAPI(title="GamePrice Scraper API")

@app.get("/scrape")
async def scrape_game_price(url: str):
    """
    Endpoint usado pelo GamePrice.Api para buscar o preço de um jogo em todas as lojas.
    O parâmetro 'url' na verdade recebe o nome do jogo vindo do C#.
    """
    if not url:
        raise HTTPException(status_code=400, detail="Nome do jogo não fornecido")
    
    # Busca o jogo em todas as plataformas em paralelo
    resultados = buscar_em_todas_lojas(url)
    
    # Retorna a lista de resultados
    return resultados

@app.get("/deals")
async def get_top_deals():
    """
    Retorna uma lista de jogos em destaque/oferta simulando uma busca rápida 
    no banco de dados (Top descontos gerais da semana).
    """
    import random
    
    # Mock realista dos maiores descontos que os bots identificariam e salvariam no BD
    deals_data = [
        { "id": 1, "title": "God of War Ragnarök", "price": "199,50", "oldPrice": "349,90", "discount": "-43%", "platform": "playstation", "store": "PS Store", "image": "https://image.api.playstation.com/vulcan/ap/rnd/202207/1210/4xJ8XB3bi888QTLZYdl7Oi0s.png" },
        { "id": 2, "title": "Cyberpunk 2077", "price": "99,90", "oldPrice": "199,90", "discount": "-50%", "platform": "xbox", "store": "Xbox", "image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1091500/header.jpg" },
        { "id": 3, "title": "Elden Ring", "price": "149,90", "oldPrice": "229,90", "discount": "-35%", "platform": "pc", "store": "Steam", "image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1245620/header.jpg" },
        { "id": 4, "title": "Hollow Knight", "price": "14,99", "oldPrice": "46,99", "discount": "-68%", "platform": "pc", "store": "GOG", "image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/367520/header.jpg" },
        { "id": 5, "title": "Red Dead Redemption 2", "price": "89,90", "oldPrice": "299,90", "discount": "-70%", "platform": "pc", "store": "Epic", "image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/1174180/header.jpg" },
        { "id": 6, "title": "The Witcher 3: Wild Hunt", "price": "19,99", "oldPrice": "99,99", "discount": "-80%", "platform": "under20", "store": "Steam", "image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/292030/header.jpg" },
        { "id": 7, "title": "Zelda: Breath of the Wild", "price": "199,00", "oldPrice": "299,00", "discount": "-33%", "platform": "nintendo", "store": "Nintendo", "image": "https://assets.nintendo.com/image/upload/c_fill,w_1200/q_auto:best/f_auto/dpr_2.0/ncom/en_US/games/switch/t/the-legend-of-zelda-breath-of-the-wild-switch/hero" },
        { "id": 8, "title": "Stardew Valley", "price": "12,49", "oldPrice": "24,99", "discount": "-50%", "platform": "under20", "store": "Steam", "image": "https://shared.akamai.steamstatic.com/store_item_assets/steam/apps/413150/header.jpg" }
    ]
    
    # Embaralha levemente para parecer dinâmico
    random.shuffle(deals_data)
    return deals_data

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
