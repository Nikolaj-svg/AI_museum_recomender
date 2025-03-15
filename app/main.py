from fastapi import FastAPI
from app.services.met_api import get_met_artwork
from app.services.wikidata import search_artworks_by_museum
from app.services.scraper import scrape_museum
from app.services.database import save_artwork

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Museum Search API is running!"}

@app.get("/met/{object_id}")
def get_met(object_id: int):
    return get_met_artwork(object_id)

@app.get("/wikidata/{museum}")
def get_wikidata(museum: str):
    return search_artworks_by_museum(museum)

@app.get("/scrape")
def get_scraped_data(url: str):
    return scrape_museum(url)

if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
