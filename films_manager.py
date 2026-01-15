from films_info import get_movie_from_omdb

class MovieManager:
    """
    Класс для хранения фильмов пользователя и управления ими.
    """
    def __init__(self):
        self.movies = []  # каждый экземпляр для одного пользователя

    def add_movie(self, title: str, status: str) -> dict | None:
        """
        Добавляет фильм по названию и статусу.
        Возвращает словарь с данными фильма или None, если фильм не найден.
        """
        movie_data = get_movie_from_omdb(title)

        if not movie_data:
            return None

        movie = {
            "title": movie_data["title"],
            "status": status,  # liked/disliked/dropped/plan_to_watch
            "genres": movie_data["genres"],
            "runtime": movie_data["runtime"],
            "imdb_rating": movie_data["imdb_rating"],
            "year": movie_data["year"]
        }

        self.movies.append(movie)
        return movie

    def get_movies(self) -> list:
        """Возвращает список всех фильмов пользователя"""
        return self.movies

    def remove_movie(self, title: str) -> bool:
        """Удаляет фильм по названию. Возвращает True, если удалён"""
        for i, movie in enumerate(self.movies):
            if movie["title"].lower() == title.lower():
                self.movies.pop(i)
                return True
        return False

    def update_status(self, title: str, new_status: str) -> bool:
        """Обновляет статус фильма. Возвращает True, если найден и обновлён"""
        for movie in self.movies:
            if movie["title"].lower() == title.lower():
                movie["status"] = new_status
                return True
        return False

    def find_movie(self, title: str) -> dict | None:
        """Ищет фильм по названию. Возвращает словарь или None"""
        for movie in self.movies:
            if movie["title"].lower() == title.lower():
                return movie
        return None