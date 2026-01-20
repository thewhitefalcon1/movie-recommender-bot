import requests
import os
from dotenv import load_dotenv

load_dotenv()
Api_Key = os.getenv('api_key')
base_url  = "http://www.omdbapi.com/"

def get_movie_from_omdb(title : str) -> dict:
  
    params = {
        't': title, 
        'apikey': Api_Key
    }
    try:
        response = requests.get(base_url, params=params, timeout=10)
        response.raise_for_status()
        data = response.json()

        if data.get("Response") == "False":
            return None

        return {
            "title": data.get("Title"),
            "year": data.get("Year"),
            "genres": data.get("Genre", "").split(", "),
            "runtime": parse_runtime(data.get("Runtime")),
            "imdb_rating": parse_rating(data.get("imdbRating"))
        }

    except requests.RequestException as e:
        print(f"Ошибка при запросе к OMDb: {e}")
        return None

def parse_runtime(runtime_str: str | None) -> int | None:
   
    if not runtime_str or runtime_str == "N/A":
        return None
    try:
        return int(runtime_str.split()[0])
    except ValueError:
        return None

def parse_rating(rating_str: str | None) -> float | None:
  
    if not rating_str or rating_str == "N/A":
        return None
    try:
        return float(rating_str)
    except ValueError:
        return None
