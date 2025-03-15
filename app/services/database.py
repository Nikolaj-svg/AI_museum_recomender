import chromadb
import requests
from googletrans import Translator
from sentence_transformers import SentenceTransformer
from app.services.wikidata import search_artworks_by_museum

# Загружаем модель для векторного поиска
model = SentenceTransformer("all-MiniLM-L6-v2")

# Подключаем ChromaDB (хранилище векторов)
db = chromadb.PersistentClient(path="data/chroma_db")
collection = db.get_or_create_collection(name="museum_data")

translator = Translator()

def translate_query(query):
    """Переводит запрос на английский перед поиском"""
    translated = translator.translate(query, src="ru", dest="en")
    return translated.text

def save_artworks_from_museum(museum_name):
    """Загружает все произведения из Wikidata и сохраняет в ChromaDB"""
    artworks = search_artworks_by_museum(museum_name)
    
    if "error" in artworks:
        return artworks  # Возвращаем ошибку, если музей не найден

    for art in artworks:
        title = art["title"]
        description = f"{art['title']} — произведение искусства, созданное {art['artist']}."
        museum = art["museum"]
        
        embedding = model.encode(description).tolist()
        collection.add(
            documents=[description],
            metadatas=[{"title": title, "museum": museum, "artist": art["artist"]}],
            embeddings=[embedding],
            ids=[str(title)]
        )

    return {"message": f"Добавлено {len(artworks)} картин из {museum_name} в базу данных."}

def search_artwork(query, top_k=5):
    """Поиск картин по базе (с заголовками и улучшенной сортировкой)"""

    query_en = translate_query(query)  # Переводим запрос на английский
    query_embedding = model.encode(query_en).tolist()

    if collection.count() == 0:
        return {"error": "База данных пуста. Добавьте картины!"}

    results = collection.query(query_embeddings=[query_embedding], n_results=top_k, include=["documents", "metadatas", "distances"])

    response = []
    if results["documents"]:
        for i in range(len(results["documents"][0])):  
            metadata = results["metadatas"][0][i]  
            title = metadata.get("title", "Без названия")
            
            # 📌 Улучшаем ранжирование — если заголовок совпадает с Mona Lisa, поднимаем выше
            boost = 0
            if "mona lisa" in title.lower():
                boost = -1  # Чем меньше число, тем выше в списке

            response.append({
                "title": title,
                "museum": metadata.get("museum", "Неизвестно"),
                "artist": metadata.get("artist", "Неизвестный автор"),
                "description": results["documents"][0][i],
                "distance": results["distances"][0][i] + boost  # Улучшаем сортировку
            })

    # 🔥 Сортируем по улучшенной дистанции (учитывая приоритет Mona Lisa)
    response.sort(key=lambda x: x["distance"])

    return response if response else {"error": "Ничего не найдено."}

