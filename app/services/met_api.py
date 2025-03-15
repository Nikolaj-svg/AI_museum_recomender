import requests

MET_API_URL = "https://collectionapi.metmuseum.org/public/collection/v1"

def get_met_artwork(object_id):
    """Получает информацию о произведении искусства из MET API"""
    url = f"{MET_API_URL}/objects/{object_id}"
    response = requests.get(url)
    if response.status_code == 200:
        data = response.json()
        return {
            "title": data.get("title", "Без названия"),
            "artist": data.get("artistDisplayName", "Неизвестный автор"),
            "date": data.get("objectDate", "Неизвестная дата"),
            "medium": data.get("medium", "Неизвестный материал"),
            "museum": "Metropolitan Museum of Art"
        }
    return {"error": "Произведение не найдено"}

# Тестируем API
if __name__ == "__main__":
    print(get_met_artwork(436121))  # Пример ID объекта
