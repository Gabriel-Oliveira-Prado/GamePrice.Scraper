# app/main.py
from fastapi import FastAPI
from fastapi.responses import JSONResponse

app = FastAPI()

@app.get("/scrape")
def scrape():
    # Sempre retorna Terraria, ignora qualquer query
    data = {
        "title": "Terraria",
        "price": "R$ 32,99",
        "url": "https://store.steampowered.com/app/105600/Terraria/"
    }
    return JSONResponse(content=data)
