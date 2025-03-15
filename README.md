# 🖼️ AI Museum Recommender

🚀 **AI Museum Recommender** — это проект, который собирает и анализирует информацию о произведениях искусства из разных музеев с помощью **Wikidata** и **Metropolitan Museum API**.

## 📌 Возможности
✅ Поиск произведений искусства в крупнейших музеях мира  
✅ Данные из **Wikidata** и **Metropolitan Museum API**  
✅ Быстрый поиск через **FastAPI**  
✅ Планируется поддержка **ML-модели** и **векторного поиска**  

## 📚 Поддерживаемые музеи
- 🏛️ **Лувр** (Louvre)  
- 🗽 **Метрополитен-музей** (Metropolitan Museum of Art)  
- 🇳🇱 **Рейксмузеум** (Rijksmuseum)  
- 🇷🇺 **Эрмитаж** (Hermitage Museum)  
- 🇬🇧 **Национальная галерея (Лондон)** (National Gallery)  
- 🇪🇸 **Музей Прадо** (Prado Museum)  
- 🇬🇧 **Тейт Британ** (Tate Britain)  
- 🇳🇱 **Музей Ван Гога** (Van Gogh Museum)  
- 🇫🇷 **Музей Орсе** (Musée d'Orsay)  
- 🇮🇹 **Галерея Уффици** (Uffizi Gallery)  

## 🛠️ Установка и запуск
### 1️⃣ Клонирование репозитория
```sh
git clone https://github.com/username/ai-museum-recommender.git
cd ai-museum-recommender

python -m venv venv
source venv/bin/activate  # macOS/Linux
venv\Scripts\activate  # Windows


pip install -r requirements.txt


uvicorn app.main:app --reload


API доступно по адресу:
📌 http://127.0.0.1:8000/docs
