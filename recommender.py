import pandas as pd
import numpy as np
from sklearn.feature_extraction.text import TfidfVectorizer


class Recommender:
    """
    Быстрая рекомендательная система:
    - жанры → numpy векторы
    - dot product для рекомендаций
    - TF-IDF для cold start
    """

    def __init__(self, dataset_path: str):
        self.df = pd.read_csv(dataset_path)

        # -------- очистка --------
        self.df["genres"] = self.df["genres"].fillna("")
        self.df["genres"] = self.df["genres"].apply(
            lambda x: [g.strip() for g in x.split(",") if g]
        )

        self.df["keywords"] = self.df["keywords"].fillna("")

        # -------- предвычисления --------
        self._prepare_genre_vectors()
        self._prepare_tfidf()

    # =========================================================
    # Основная рекомендация (FAST)
    # =========================================================
    def recommend(self, profile: dict, top_n: int = 10):
        preferred_genres = profile.get("preferred_genres", [])

        if not preferred_genres:
            return []

        user_vector = self._build_user_vector(preferred_genres)
        scores = self.movie_genre_matrix @ user_vector

        top_idx = np.argsort(scores)[-top_n:][::-1]

        return self.df.iloc[top_idx][
            ["title", "release_date", "vote_average", "runtime", "genres"]
        ].to_dict("records")

    # =========================================================
    # Cold start (TF-IDF)
    # =========================================================
    def recommend_by_keywords(self, query: str, top_n: int = 10):
        query_vec = self.tfidf.transform([query])
        scores = (self.keyword_matrix @ query_vec.T).toarray().ravel()

        top_idx = np.argsort(scores)[-top_n:][::-1]

        return self.df.iloc[top_idx][
            ["title", "release_date", "vote_average", "keywords"]
        ].to_dict("records")

    # =========================================================
    # Векторы жанров (ОДИН РАЗ)
    # =========================================================
    def _prepare_genre_vectors(self):
        all_genres = sorted(
            {g for genres in self.df["genres"] for g in genres}
        )

        self.genre_to_idx = {g: i for i, g in enumerate(all_genres)}

        matrix = np.zeros((len(self.df), len(all_genres)), dtype=np.uint8)

        for i, genres in enumerate(self.df["genres"]):
            for g in genres:
                matrix[i, self.genre_to_idx[g]] = 1

        self.movie_genre_matrix = matrix

    def _build_user_vector(self, preferred_genres: list[str]) -> np.ndarray:
        vec = np.zeros(len(self.genre_to_idx), dtype=np.uint8)
        for g in preferred_genres:
            if g in self.genre_to_idx:
                vec[self.genre_to_idx[g]] = 1
        return vec

    # =========================================================
    # TF-IDF
    # =========================================================
    def _prepare_tfidf(self):
        self.tfidf = TfidfVectorizer(
            stop_words="english",
            max_features=3000
        )
        self.keyword_matrix = self.tfidf.fit_transform(self.df["keywords"])
