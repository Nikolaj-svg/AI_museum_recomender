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
    "uffizi gallery": "Q394527",
    "british museum": "Q6373",
    "museo reina sofia": "Q160236",
    "guggenheim museum new york": "Q151828",
    "museum of modern art": "Q188740",
    "national gallery of art": "Q214867",
    "victoria and albert museum": "Q185372",
    "musei vaticani": "Q1067274",
    "tokyo national museum": "Q1132583",
    "los angeles county museum of art": "Q130468",
    "art institute of chicago": "Q213342",
    "tretyakov gallery": "Q196189",
    "pompidou centre": "Q193597",
    "national museum of china": "Q236684",
    "musée rodin": "Q152357",
    "musée picasso": "Q3404354",
    "museo thyssen-bornemisza": "Q160240",
    "musée du quai branly": "Q1037598",
    "national museum of western art": "Q1132587",
    "museum of fine arts boston": "Q49135",
    "getty center": "Q201589",
    "san francisco museum of modern art": "Q49136",
    "museum of fine arts houston": "Q488197",
    "philadelphia museum of art": "Q49137",
    "museum of contemporary art los angeles": "Q314162",
    "national museum of korea": "Q1258097",
    "israel museum": "Q190608",
    "museum of contemporary art tokyo": "Q1132589",
    "boijmans van beuningen museum": "Q679527",
    "museum of contemporary art chicago": "Q1996562",
    "serpentine gallery": "Q920732",
    "tate modern": "Q159424",
    "frick collection": "Q153978",
    "national portrait gallery london": "Q206358",
    "brooklyn museum": "Q49095",
    "musée de l'orangerie": "Q152357",
    "stadel museum": "Q163091",
    "peggy guggenheim collection": "Q179195",
    "musée guimet": "Q1651423",
    "museo nacional de bellas artes argentina": "Q824304",
    "museo soumaya": "Q181745",
    "museo de arte moderno mexico": "Q1730070",
    "lenbachhaus": "Q656287",
    "museo botero": "Q1128652",
    "musée granet": "Q3661722",
    "poldi pezzoli museum": "Q385349",
    "museo nacional de san carlos": "Q2196141",
    "museo de arte de lima": "Q491938",
    "art gallery of ontario": "Q196601",
    "national museum stockholm": "Q613320",
    "museum of modern art warsaw": "Q834497",
    "museo tamayo": "Q688619",
    "museo barroco": "Q607019",
    "musée d'art contemporain de lyon": "Q1024315",
    "musée de l'école de nancy": "Q3367463",
    "museo nacional de colombia": "Q900891",
    "museo nacional de bellas artes chile": "Q901264",
    "museo de arte de puerto rico": "Q1783092",
    "national museum prague": "Q108705",
    "museo nacional de antropología mexico": "Q193108",
    "kiasma": "Q181763",
    "museo nazionale romano": "Q1201740",
    "museo del prado": "Q160112",
    "museo di capodimonte": "Q756034",
    "museo archeologico nazionale di napoli": "Q153978",
    "galleria dell'accademia": "Q198944",
    "museo del novecento": "Q1450364",
    "museo etrusco guarnacci": "Q1051540",
    "galleria d'arte moderna palermo": "Q3952589",
    "museo nazionale di san marco": "Q3192432",
    "museo di san martino": "Q1667589",
    "museo di storia naturale di firenze": "Q1678696",
    "museo nazionale della scienza e della tecnologia leonardo da vinci": "Q368508",
    "museo storico nazionale dell'artiglieria": "Q3612084",
    "museo nazionale del cinema": "Q1193941",
    "museo dell'automobile": "Q1193961",
    "museo de la revolución": "Q930562",
    "museo de la ciudad de méxico": "Q1674468",
    "museo de bellas artes de valencia": "Q1712554",
    "museo de la alhambra": "Q3293577",
    "museo de arte contemporáneo de barcelona": "Q160112",
    "museo de bellas artes de sevilla": "Q1775031",
    "museo de bellas artes de córdoba": "Q2076306",
    "museo de bellas artes de bilbao": "Q2013303",
    "museo arqueológico nacional de españa": "Q159115",
    "museo de cera de madrid": "Q612264",
    "museo de la evolución humana": "Q1104997"
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
    LIMIT 200
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
