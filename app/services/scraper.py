import requests
from bs4 import BeautifulSoup

def scrape_museum(url):
    """Парсит страницу музея и получает список картин"""
    headers = {"User-Agent": "Mozilla/5.0"}
    response = requests.get(url, headers=headers)
    
    if response.status_code == 200:
        soup = BeautifulSoup(response.text, "html.parser")
        artworks = []
        
        for item in soup.find_all("div", class_="artwork-card"):
            title = item.find("h2").text.strip() if item.find("h2") else "Без названия"
            description = item.find("p").text.strip() if item.find("p") else "Нет описания"
            artworks.append({"title": title, "description": description})
        
        return artworks
    return {"error": "Не удалось получить данные"}

# Тестим
if __name__ == "__main__":
    print(scrape_museum("https://www.louvre.fr/en/explore"))
