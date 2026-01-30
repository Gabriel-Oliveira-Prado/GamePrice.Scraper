from fastapi import APIRouter
from fastapi.responses import JSONResponse

router = APIRouter()

@router.get("/scrape")
def scrape():
    # Dados de teste fixos
    data = {
        "title": "Terraria",
        "price": "R$ 32,99",
        "url": "https://store.steampowered.com/app/105600/Terraria/"
    }
    return JSONResponse(content=data)
