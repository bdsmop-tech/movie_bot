# Локальный каталог на русском вместо внешних API.
# Здесь только утилиты работы с локальным JSON и построение URL для трейлера (поисковый запрос YouTube).

import json, os, math, urllib.parse

CAT_PATH = os.path.join(os.path.dirname(__file__), "catalog_ru.json")

def load_catalog():
    with open(CAT_PATH, "r", encoding="utf-8") as f:
        return json.load(f)

def get_genres(content_type="movie"):
    data = load_catalog()
    return data["genres"].get(content_type, [])

def discover(content_type="movie", genre_ids=None, min_rating=0.0, min_year=1900, page=1, page_size=20):
    data = load_catalog()
    items = [x for x in data["items"] if x["type"] == content_type]
    if genre_ids:
        genre_ids = set(genre_ids)
        items = [x for x in items if genre_ids.intersection(set(x["genre_ids"]))]
    items = [x for x in items if (x.get("rating",0) >= min_rating and x.get("year",0) >= min_year)]
    # сортировка по рейтингу убыв
    items.sort(key=lambda x: (x.get("rating",0), x.get("year",0)), reverse=True)
    # пагинация
    start = (page-1)*page_size
    end = start + page_size
    return items[start:end]

def youtube_search_url(query: str):
    q = urllib.parse.quote_plus(query)
    return f"https://www.youtube.com/results?search_query={q}"
