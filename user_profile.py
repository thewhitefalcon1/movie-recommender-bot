from collections import Counter
from typing import List, Dict, Optional


class UserProfile:
    """
    Формирует профиль пользователя на основе его оценок фильмов.
    """

    def __init__(self, movies: List[Dict]):
        self.movies = movies
        self.profile = self._build_profile()

    def _build_profile(self) -> Dict:
        liked = [m for m in self.movies if m["status"] == "liked"]
        disliked = [m for m in self.movies if m["status"] == "disliked"]

        if not liked:
            return {
                "preferred_genres": [],
                "disliked_genres": [],
                "avg_runtime": None,
                "min_rating": None,
                "is_empty": True
            }

        # --- ЖАНРЫ ---
        liked_genres = [
            genre for m in liked for genre in m.get("genres", [])
        ]
        disliked_genres = [
            genre for m in disliked for genre in m.get("genres", [])
        ]

        top_liked = [g for g, _ in Counter(liked_genres).most_common(5)]
        top_disliked = [g for g, _ in Counter(disliked_genres).most_common(5)]

        # --- ДЛИТЕЛЬНОСТЬ ---
        runtimes = [
            m["runtime"] for m in liked
            if m.get("runtime") is not None
        ]
        avg_runtime = round(sum(runtimes) / len(runtimes), 1) if runtimes else None

        # --- РЕЙТИНГ ---
        ratings = [
            m["imdb_rating"] for m in liked
            if m.get("imdb_rating") is not None
        ]
        min_rating = min(ratings) if ratings else None

        return {
            "preferred_genres": top_liked,
            "disliked_genres": top_disliked,
            "avg_runtime": avg_runtime,
            "min_rating": min_rating,
            "is_empty": False
        }

    def get_profile(self) -> Dict:
        return self.profile
