from collections import Counter
from typing import List

class UserProfile:
    """
    Анализ предпочтений пользователя на основе его фильмов
    """
    def __init__(self, movies: List[dict]):
        self.movies = movies
        self.profile = self._build_profile()

    def _build_profile(self):
        liked_movies = [m for m in self.movies if m["status"] == "liked"]
        if not liked_movies:
            return {
                "preferred_genres": [],
                "avg_runtime": None,
                "min_rating": None
            }

        # Жанры
        genres = [genre for m in liked_movies for genre in m["genres"]]
        top_genres = [g for g, _ in Counter(genres).most_common(5)]

        # Средняя длительность
        runtimes = [m["runtime"] for m in liked_movies if m["runtime"] is not None]
        avg_runtime = round(sum(runtimes)/len(runtimes), 1) if runtimes else None

        # Минимальный рейтинг
        ratings = [m["imdb_rating"] for m in liked_movies if m["imdb_rating"] is not None]
        min_rating = min(ratings) if ratings else None

        return {
            "preferred_genres": top_genres,
            "avg_runtime": avg_runtime,
            "min_rating": min_rating
        }

    def get_profile(self):
        return self.profile
