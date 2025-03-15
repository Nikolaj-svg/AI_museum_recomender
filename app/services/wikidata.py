import requests

WIKIDATA_SPARQL_URL = "https://query.wikidata.org/sparql"

MUSEUM_QID = {
    "louvre": "Q19675",
    "metropolitan museum of art": "Q160236",
    "rijksmuseum": "Q190804",
    "hermitage museum": "Q132783",
    "national gallery": "Q180788",
    "prado museum": "Q160112",
    "tate britain": "Q192236",
    "van gogh museum": "Q159949",
    "musée d'orsay": "Q190124",
    "uffizi gallery": "Q394527"
}

def search_artworks_by_museum(museum_name):
    """Запрашивает произведения искусства в указанном музее через Wikidata"""
    formatted_name = museum_name.lower().replace("_", " ")

    if formatted_name not in MUSEUM_QID:
        return {"error": f"Музей не найден. Доступные музеи: {', '.join(MUSEUM_QID.keys())}"}

    museum_qid = MUSEUM_QID[formatted_name]

    query = f"""
    SELECT ?artwork ?artworkLabel ?creatorLabel WHERE {{
      ?artwork wdt:P31 wd:Q3305213;
               wdt:P170 ?creator;
               wdt:P276 wd:{museum_qid}.
      SERVICE wikibase:label {{ bd:serviceParam wikibase:language "en". }}
    }}
    LIMIT 20
    """
    headers = {"User-Agent": "MuseumDataCollector/1.0"}
    response = requests.get(WIKIDATA_SPARQL_URL, params={"query": query, "format": "json"}, headers=headers)

    if response.status_code == 200:
        data = response.json()
        results = []
        for item in data["results"]["bindings"]:
            results.append({
                "title": item["artworkLabel"]["value"],
                "artist": item.get("creatorLabel", {}).get("value", "Неизвестный автор"),
                "museum": museum_name
            })
        return results

    return {"error": f"Ошибка запроса: {response.status_code}"}
