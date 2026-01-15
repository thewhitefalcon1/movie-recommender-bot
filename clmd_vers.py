# cli.py
from films_manager import MovieManager

def main():
    manager = MovieManager()

    while True:
        print("\n=== Менеджер фильмов ===")
        print("1. Добавить фильм")
        print("2. Показать фильмы")
        print("3. Обновить статус фильма")
        print("4. Удалить фильм")
        print("5. Выйти")

        choice = input("Выберите действие: ")

        if choice == "1":
            title = input("Введите название фильма: ")
            status = input(
                "Введите статус (liked/disliked/dropped/plan_to_watch): "
            )
            movie = manager.add_movie(title, status)
            if movie:
                print(f"Фильм '{movie['title']}' добавлен")
            else:
                print("Фильм не найден в OMDb")

        elif choice == "2":
            movies = manager.get_movies()
            if not movies:
                print("Список фильмов пуст")
            else:
                print("\nВаши фильмы:")
                for i, m in enumerate(movies, 1):
                    print(
                        f"{i}. {m['title']} ({m['year']}) | "
                        f"{m['status']} | ⭐ {m['imdb_rating']} | "
                        f"{', '.join(m['genres'])}"
                    )

        elif choice == "3":
            title = input("Введите название фильма для изменения статуса: ")
            new_status = input(
                "Введите новый статус (liked/disliked/dropped/plan_to_watch): "
            )
            if manager.update_status(title, new_status):
                print("Статус обновлён")
            else:
                print("Фильм не найден")

        elif choice == "4":
            title = input("Введите название фильма для удаления: ")
            if manager.remove_movie(title):
                print("Фильм удалён")
            else:
                print("Фильм не найден")

        elif choice == "5":
            print("До свидания!")
            break

        else:
            print("Неверный выбор, попробуйте снова")

if __name__ == "__main__":
    main()
