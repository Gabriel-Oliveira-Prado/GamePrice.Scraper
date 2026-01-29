from fastapi import APIRouter
from app.services.generic import scrape_basic_info

router = APIRouter(prefix="/scrape", tags=["Scraping"])


@router.get("/")
def scrape():
    url = "https://store.steampowered.com/app/105600/Terraria/"
    return scrape_basic_info(url)