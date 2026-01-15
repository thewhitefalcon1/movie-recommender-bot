import pandas as pd
import numpy as np

from sklearn.metrics.pairwise import cosine_similarity
from sklearn.feature_extraction.text import TfidfVectorizer


class Recommender:
    """
    Рекомендательная система:
    - cosine similarity по профилю
    - TF-IDF + cosine для cold start
    """

    GENRE_WEIGHT = 0.6
    RATING_WEIGHT = 0.25
    RUNTIME_WEIGHT = 0.15

    def __init__(self, dataset_path: str):
        self.df = pd.read_csv('TMDB_movie_dataset_v11.csv')

        # --- Очистка ---
        self.df["genres"] = self.df["genres"].fillna("")
        self.df["genres"] = self.df["genres"].apply(
            lambda x: [g.strip() for g in x.split(",") if g]
        )

        self.df["keywords"] = self.df["keywords"].fillna("")
        self.df["runtime"] = pd.to_numeric(self.df["runtime"], errors="coerce")
        self.df["vote_average"] = pd.to_numeric(self.df["vote_average"], errors="coerce")

        # --- TF-IDF для cold start ---
        self._prepare_tfidf()

    # =========================================================
    # Основной метод
    # =========================================================
    def recommend(self, profile: dict, top_n: int = 10):
        if profile.get("is_empty"):
            raise ValueError("Профиль пуст — используйте recommend_by_keywords")

        movie_vectors = []
        for _, row in self.df.iterrows():
            movie_vectors.append(self._movie_vector(row, profile))

        movie_vectors = np.array(movie_vectors)
        user_vector = self._user_vector(profile)

        similarities = cosine_similarity(
            [user_vector], movie_vectors
        )[0]

        self.df["similarity"] = similarities

        return (
            self.df.sort_values("similarity", ascending=False)
            .head(top_n)[
                ["title", "release_date", "vote_average", "runtime", "genres"]
            ]
            .to_dict("records")
        )

    # =========================================================
    # Cold start (ключевые слова)
    # =========================================================
    def recommend_by_keywords(self, query: str, top_n: int = 10):
        query_vec = self.tfidf.transform([query])
        similarities = cosine_similarity(
            query_vec, self.keyword_matrix
        )[0]

        self.df["similarity"] = similarities

        return (
            self.df.sort_values("similarity", ascending=False)
            .head(top_n)[
                ["title", "release_date", "vote_average", "keywords"]
            ]
            .to_dict("records")
        )

    # =========================================================
    # Векторы
    # =========================================================
    def _movie_vector(self, movie: pd.Series, profile: dict) -> np.ndarray:
        # --- ЖАНРЫ ---
        liked_score = sum(
            1 for g in movie["genres"]
            if g in profile["preferred_genres"]
        )
        disliked_score = sum(
            1 for g in movie["genres"]
            if g in profile["disliked_genres"]
        )

        genre_score = liked_score - disliked_score

        # --- РЕЙТИНГ ---
        rating = movie["vote_average"] if not np.isnan(movie["vote_average"]) else 0

        # --- ДЛИТЕЛЬНОСТЬ ---
        runtime = movie["runtime"]
        if np.isnan(runtime):
            runtime = profile["avg_runtime"] or 0

        return np.array([
            genre_score * self.GENRE_WEIGHT,
            rating * self.RATING_WEIGHT,
            runtime * self.RUNTIME_WEIGHT
        ])

    def _user_vector(self, profile: dict) -> np.ndarray:
        genre_pref_strength = len(profile["preferred_genres"])

        return np.array([
            genre_pref_strength * self.GENRE_WEIGHT,
            (profile["min_rating"] or 0) * self.RATING_WEIGHT,
            (profile["avg_runtime"] or 0) * self.RUNTIME_WEIGHT
        ])

    # =========================================================
    # TF-IDF
    # =========================================================
    def _prepare_tfidf(self):
        self.tfidf = TfidfVectorizer(
            stop_words="english",
            max_features=5000
        )
        self.keyword_matrix = self.tfidf.fit_transform(self.df["keywords"])
