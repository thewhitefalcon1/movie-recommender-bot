import os
from telebot import TeleBot, types
from dotenv import load_dotenv

from films_manager import MovieManager
from user_profile import UserProfile
from recommender import Recommender

# --- Инициализация ---
load_dotenv()
TOKEN = os.getenv("TELEGRAM_TOKEN")

bot = TeleBot(TOKEN)
rec_engine = Recommender("TMDB_movie_dataset_v11.csv")

# chat_id -> MovieManager
user_managers = {}


# =========================================================
# START / MENU
# =========================================================
@bot.message_handler(commands=["start"])
def start(message):
    chat_id = message.chat.id
    user_managers.setdefault(chat_id, MovieManager())
    send_main_menu(chat_id)


def send_main_menu(chat_id):
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True)
    markup.add("➕ Добавить фильм", "📄 Список фильмов")
    markup.add("✏️ Обновить статус", "🗑 Удалить фильм")
    markup.add("🎯 Рекомендации")
    bot.send_message(chat_id, "Главное меню:", reply_markup=markup)


# =========================================================
# MENU HANDLER
# =========================================================
@bot.message_handler(func=lambda m: True)
def menu_handler(message):
    chat_id = message.chat.id
    text = message.text
    manager = user_managers.setdefault(chat_id, MovieManager())

    if text == "➕ Добавить фильм":
        msg = bot.send_message(
            chat_id,
            "Введите: название, статус\n"
            "Статусы: liked / disliked / want / dropped"
        )
        bot.register_next_step_handler(msg, add_movie_step)

    elif text == "📄 Список фильмов":
        show_movies(chat_id)

    elif text == "🗑 Удалить фильм":
        show_movies(chat_id, delete=True)

    elif text == "✏️ Обновить статус":
        show_movies(chat_id, update=True)

    elif text == "🎯 Рекомендации":
        handle_recommendations(chat_id)

    else:
        send_main_menu(chat_id)


# =========================================================
# ADD MOVIE
# =========================================================
def add_movie_step(message):
    chat_id = message.chat.id
    manager = user_managers[chat_id]

    try:
        title, status = [x.strip() for x in message.text.split(",")]
        movie = manager.add_movie(title, status)

        if movie:
            bot.send_message(chat_id, f"✅ Фильм «{movie['title']}» добавлен")
        else:
            bot.send_message(chat_id, "❌ Фильм не найден в OMDb")

    except ValueError:
        bot.send_message(chat_id, "❌ Формат: название, статус")

    send_main_menu(chat_id)


# =========================================================
# SHOW MOVIES
# =========================================================
def show_movies(chat_id, delete=False, update=False):
    manager = user_managers[chat_id]
    movies = manager.get_movies()

    if not movies:
        bot.send_message(chat_id, "Список фильмов пуст")
        send_main_menu(chat_id)
        return

    markup = types.InlineKeyboardMarkup()
    for m in movies:
        label = f"{m['title']} ({m['status']})"

        if delete:
            markup.add(types.InlineKeyboardButton(label, callback_data=f"del:{m['title']}"))
        elif update:
            markup.add(types.InlineKeyboardButton(label, callback_data=f"upd:{m['title']}"))
        else:
            markup.add(types.InlineKeyboardButton(label, callback_data="noop"))

    bot.send_message(chat_id, "Ваши фильмы:", reply_markup=markup)


# =========================================================
# INLINE BUTTONS
# =========================================================
@bot.callback_query_handler(func=lambda call: True)
def callback_handler(call):
    chat_id = call.message.chat.id
    manager = user_managers[chat_id]

    if call.data.startswith("del:"):
        title = call.data.split(":", 1)[1]
        manager.remove_movie(title)
        bot.answer_callback_query(call.id, f"Удалено: {title}")
        show_movies(chat_id, delete=True)

    elif call.data.startswith("upd:"):
        title = call.data.split(":", 1)[1]
        msg = bot.send_message(chat_id, f"Введите новый статус для «{title}»:")
        bot.register_next_step_handler(msg, lambda m, t=title: update_status_step(m, t))

    bot.edit_message_reply_markup(chat_id, call.message.message_id, reply_markup=None)


def update_status_step(message, title):
    chat_id = message.chat.id
    manager = user_managers[chat_id]

    manager.update_status(title, message.text.strip())
    bot.send_message(chat_id, f"Статус фильма «{title}» обновлён")
    send_main_menu(chat_id)


# =========================================================
# RECOMMENDATIONS
# =========================================================
def handle_recommendations(chat_id):
    manager = user_managers[chat_id]
    profile = UserProfile(manager.get_movies()).get_profile()

    # --- Cold start ---
    if profile.get("is_empty"):
        msg = bot.send_message(
            chat_id,
            "У вас пока нет понравившихся фильмов.\n"
            "Введите ключевые слова (например: space, future, war):"
        )
        bot.register_next_step_handler(msg, recommend_by_keywords)
        return

    # --- Normal recommendations ---
    recommendations = rec_engine.recommend(profile, top_n=5)
    send_recommendation_text(chat_id, recommendations)


def recommend_by_keywords(message):
    chat_id = message.chat.id
    query = message.text.strip()

    recommendations = rec_engine.recommend_by_keywords(query, top_n=5)
    send_recommendation_text(chat_id, recommendations)


def send_recommendation_text(chat_id, recommendations):
    if not recommendations:
        bot.send_message(chat_id, "Подходящих фильмов не найдено 😔")
        send_main_menu(chat_id)
        return

    text = "🎬 Рекомендации для вас:\n\n"
    for i, m in enumerate(recommendations, 1):
        text += (
            f"{i}. {m['title']}\n"
        )

    bot.send_message(chat_id, text)
    send_main_menu(chat_id)


# =========================================================
# RUN
# =========================================================
print('bot is working')
bot.polling()