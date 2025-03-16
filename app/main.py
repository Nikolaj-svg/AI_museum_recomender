from fastapi import FastAPI
from app.services.database import collection, search_artwork, save_artworks_from_museum
import together
import re
import os
from dotenv import load_dotenv

load_dotenv()
together.api_key = os.getenv("TOGETHER_API_KEY")

app = FastAPI()

@app.get("/")
def read_root():
    return {"message": "Museum Search API is running!"}

def filter_relevant_info(search_results):
    """
    Фильтрует результаты поиска, оставляя только самые релевантные данные.
    """
    filtered = []
    for res in search_results:
        if res.get('description'):  # Оставляем только объекты с описанием
            filtered.append({
                "title": res.get("title", "Без названия"),
                "museum": res.get("museum", "Неизвестно"),
                "description": res["description"]
            })
    
    return filtered[:5]  # Ограничиваем количество релевантных записей

@app.get("/clarify")
def clarify_query(query: str):
    """Обрабатывает непонятные запросы и предлагает варианты"""
    
    # 1️⃣ Проверяем, есть ли в запросе ключевые слова
    query_lower = query.lower()
    
    keywords_painting = ["картина", "изображено", "автор", "стиль"]
    keywords_artist = ["художник", "какие работы", "написал", "техники", "биография"]
    keywords_museum = ["музей", "экспозиция", "находится", "собрание"]
    
    # 2️⃣ Определяем категорию запроса
    if any(word in query_lower for word in keywords_painting):
        return {"query": query, "answer": "Вы спрашиваете о картине, но ваш вопрос немного неполный. Попробуйте уточнить!"}
    
    if any(word in query_lower for word in keywords_artist):
        return {"query": query, "answer": "Вы спрашиваете о художнике! Вы хотите узнать биографию или его известные картины?"}

    if any(word in query_lower for word in keywords_museum):
        return {"query": query, "answer": "Вы спрашиваете о музее! Хотите узнать, какие картины там выставлены?"}

    # 3️⃣ Если вопрос совсем странный, предлагаем идеи
    random_suggestions = [
        "Какая картина вдохновила больше всего людей?",
        "Как художники эпохи Ренессанса создавали свои работы?",
        "Какие картины считаются самыми загадочными в истории?",
        "Какой музей стоит посетить в первую очередь?",
    ]

    return {
        "query": query,
        "answer": "Ваш вопрос кажется необычным! Возможно, вас интересует что-то из этого списка?",
        "suggestions": random_suggestions
    }


@app.get("/ask")
def ask_museum(query: str):
    """Обрабатывает запрос пользователя и ищет информацию в базе данных + Together AI"""

    # 1️⃣ Определяем, о чем спрашивают (картина, художник, музей, биография, история искусства и т.д.)
    query_lower = query.lower()
    query_type = None

    if "кто нарисовал" in query_lower or "автор" in query_lower:
        query_type = "artist"
    elif "какие картины написал" in query_lower:
        query_type = "artist_paintings"
    elif "что экспонируется" in query_lower or "какие картины есть" in query_lower:
        query_type = "museum_paintings"
    elif "расскажи про картину" in query_lower:
        query_type = "artwork"
    elif "какие техники использовал" in query_lower:
        query_type = "artist_info"
    elif "биография" in query_lower or "кем был" in query_lower or "биографию" in query_lower or "карьера" in query_lower or "карьеру" in query_lower:
        query_type = "artist_biography"
    elif "какая картина вдохновила" in query_lower or "самая загадочная картина" in query_lower:
        query_type = "art_mystery"
    elif "как создавали работы" in query_lower or "эпоха ренессанса" in query_lower:
        query_type = "art_history"
    elif "какой музей стоит посетить" in query_lower:
        query_type = "museum_recommendation"

    # Если ничего не поняли — идем к обработчику странных запросов
    if query_type is None:
        return clarify_query(query)

    # 2️⃣ Ищем в базе данных ChromaDB
    search_results = search_artwork(query)
    filtered_results = filter_relevant_info(search_results)

    if filtered_results:
        context = "\n".join([
            f"{res['title']} ({res['museum']}): {res['description']}"
            for res in filtered_results
        ])
    else:
        context = "Нет найденных данных. Ответь по общим знаниям."

    # 3️⃣ Формируем запрос в Together AI в зависимости от типа запроса
    query_prompts = {
        "artist": f"Кто является автором картины '{query}'? Дай развернутый ответ с биографией художника.",
        "artist_paintings": f"Какие картины написал художник {query.replace('какие картины написал ', '')}? Дай список с кратким описанием.",
        "museum_paintings": f"Какие картины можно увидеть в музее {query.replace('что экспонируется в ', '')}? Дай список с краткими описаниями.",
        "artwork": f"Расскажи про картину '{query.replace('расскажи про картину ', '')}'. Дай полное описание с историей создания, стилем и значением.",
        "artist_info": f"Какие техники использовал художник {query.replace('какие техники использовал ', '')}? Опиши подробно.",
        "artist_biography": f"Расскажи подробно о жизни и карьере художника {query.replace('биография ', '').replace('расскажи про ', '')}.",
        "art_mystery": "Какие картины считаются самыми загадочными? Объясни, почему.",
        "art_history": "Как художники эпохи Ренессанса создавали свои работы? Опиши процесс и влияние.",
        "mona_lisa": "Почему картина «Мона Лиза» стала такой популярной? Дай краткую историю и интересные факты.",
        "museum_recommendation": "Какой музей стоит посетить в первую очередь, если интересуешься искусством?"
    }
    
    prompt = query_prompts.get(query_type, f"Ответь на вопрос: {query}. Используй предоставленные данные.")

    if "Нет найденных данных" in context:
        prompt = f"Объясни тему '{query}' с нуля, как эксперт по искусству."

    # 4️⃣ Отправляем запрос в Together AI
    response = together.Complete.create(
        model="mistralai/Mistral-7B-Instruct-v0.1",
        prompt=(
            "Ты — искусствовед и историк. Ответь на вопрос максимально подробно, используя точные исторические данные.\n\n"
            f"🔍 Вопрос: {query}\n\n"
            f"🎨 Контекст:\n{context}\n\n"
            "📢 Дай полный ответ **на русском языке**:"
        ),
        max_tokens=600,
        temperature=0.5
    )

    print("Together AI Response:", response)

    if "choices" not in response or not response["choices"] or not response["choices"][0]["text"].strip():
        return {"query": query, "answer": "Ошибка запроса к Together AI — ответ пустой.", "debug": response}

    answer_text = response["choices"][0]["text"]

    # 5️⃣ Очищаем текст от лишних скобок и комментариев
    clean_answer = re.sub(r'\{.*?\}', '', answer_text).strip()

    return {"query": query, "answer": clean_answer}




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

    all_artworks = collection.get(include=["metadatas", "documents"], limit=50)
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
