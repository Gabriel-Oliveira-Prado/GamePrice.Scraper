from fastapi import FastAPI, HTTPException
import uvicorn
from app.scraping_steam.scraping_games import buscar_jogo_exato

app = FastAPI(title="GamePrice Scraper API")

@app.get("/scrape")
async def scrape_game_price(url: str):
    """
    Endpoint usado pelo GamePrice.Api para buscar o preço de um jogo.
    O parâmetro 'url' na verdade recebe o nome do jogo vindo do C#.
    """
    if not url:
        raise HTTPException(status_code=400, detail="Nome do jogo não fornecido")
    
    # Busca o jogo na Steam (usando a função existente)
    resultado = buscar_jogo_exato(url)
    
    if not resultado:
        raise HTTPException(status_code=404, detail="Jogo não encontrado")

    # Mapear para o formato que a GamePriceDto no C# espera: title, price, url
    return {
        "title": resultado["nome"],
        "price": resultado["preco_atual"],
        "url": resultado["url"]
    }

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
