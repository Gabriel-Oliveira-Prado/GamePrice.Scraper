from fastapi import FastAPI
from app.routers.scraping import router as scraping_router

app = FastAPI(title="GamePrice Scraper")

app.include_router(scraping_router)


@app.get("/")
def root():
    return {"message": "API online"}
