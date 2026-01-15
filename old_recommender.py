# recommender.py
import pandas as pd

class Recommender:
    """
    Генерирует рекомендации на основе профиля пользователя
    и TMDb Dataset.
    """
    def __init__(self, dataset_path: str):
        self.df = pd.read_csv('TMDB_movie_dataset_v11.csv')
        # Преобразуем жанры в список
        self.df['genres'] = self.df['genres'].fillna('')
        self.df['genres'] = self.df['genres'].apply(lambda x: [g.strip() for g in x.split(',') if g])

    def recommend(self, profile: dict, top_n=10, sort_by='popularity'):
        """
        Возвращает top_n фильмов, подходящих под профиль
        sort_by: popularity, vote_average, runtime
        """
        df = self.df.copy()

        # Фильтр по жанрам
        preferred_genres = profile.get('preferred_genres', [])
        if preferred_genres:
            df = df[df['genres'].apply(lambda gs: any(g in gs for g in preferred_genres))]

        # Фильтр по длительности
        avg_runtime = profile.get('avg_runtime')
        if avg_runtime:
            df = df[df['runtime'].notna()]
            df = df[(df['runtime'] >= avg_runtime - 20) & (df['runtime'] <= avg_runtime + 20)]

        # Фильтр по рейтингу IMDb
        min_rating = profile.get('min_rating')
        if min_rating:
            df = df[df['vote_average'].notna()]
            df = df[df['vote_average'] >= min_rating]

        # Сортировка
        if sort_by in ['popularity', 'vote_average', 'runtime']:
            df = df.sort_values(by=sort_by, ascending=False)

        # Возврат топ-n
        recommendations = df.head(top_n)[['title', 'release_date', 'vote_average', 'runtime', 'genres']].to_dict('records')
        return recommendations
