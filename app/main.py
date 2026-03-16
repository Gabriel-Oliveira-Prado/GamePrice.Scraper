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
    
    # Busca o jogo em todas as plataformas
    resultados = buscar_em_todas_lojas(url)
    
    # Retorna o dicionário com resultados de todas as lojas
    return resultados

if __name__ == "__main__":
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
