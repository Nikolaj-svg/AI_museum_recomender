from fastapi import FastAPI
from app.services.met_api import get_met_artwork
from app.services.wikidata import search_artworks_by_museum
from app.services.database import collection
from app.services.scraper import scrape_museum
from app.services.database import search_artwork, save_artworks_from_museum

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Museum Search API is running!"}


@app.get("/met/{object_id}")
def get_met(object_id: int):
    return get_met_artwork(object_id)

@app.delete("/delete_artwork/{title}")
def delete_artwork(title: str):
    """Удаляет произведение искусства по заголовку"""
    results = collection.get(include=["metadatas"], where={"title": title})
    
    if results["metadatas"]:
        collection.delete(where={"title": title})
        return {"message": f"Удалено произведение: {title}"}
    else:
        return {"error": f"Произведение с заголовком '{title}' не найдено в базе."}

@app.delete("/clear_database")
def clear_database():
    """Полностью очищает базу данных"""
    all_data = collection.get(include=["metadatas"])  # Получаем метаданные всех записей
    if not all_data["metadatas"]:
        return {"message": "База данных уже пуста."}

    all_ids = [meta["title"] for meta in all_data["metadatas"] if "title" in meta]  # Берём title как ID

    if all_ids:
        collection.delete(where={"title": {"$in": all_ids}})  # Удаляем по заголовкам

    return {"message": "База данных полностью очищена."}




@app.get("/wikidata/{museum}")
def get_wikidata(museum: str):
    return search_artworks_by_museum(museum)

@app.get("/scrape")
def get_scraped_data(url: str):
    return scrape_museum(url)

@app.get("/search")
def search_museum(query: str):
    """Поиск картин по базе данных (ChromaDB)"""
    results = search_artwork(query)
    return {"query": query, "results": results}

@app.post("/load_museum/{museum_name}")
def load_museum_data(museum_name: str):
    """Загружает все картины из музея в базу данных"""
    return save_artworks_from_museum(museum_name)

@app.get("/list_artworks")
def list_artworks():
    """Выводит все произведения, сохраненные в базе данных"""
    if collection.count() == 0:
        return {"error": "База данных пуста."}

    all_artworks = collection.get(include=["metadatas", "documents"], limit=50)  # Получаем 50 записей
    response = []
    
    for i in range(len(all_artworks["documents"])):
        metadata = all_artworks["metadatas"][i]
        response.append({
            "title": metadata.get("title", "Без названия"),
            "museum": metadata.get("museum", "Неизвестно"),
            "artist": metadata.get("artist", "Неизвестный автор"),
            "description": all_artworks["documents"][i]
        })

    return response


if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="127.0.0.1", port=8000)
