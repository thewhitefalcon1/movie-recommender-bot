import requests
import os


class TitleResolver:
    """
    Определяет оригинальное (английское) название фильма
    по русскому названию с помощью GigaChat
    """

    API_URL = "https://gigachat.devices.sberbank.ru/api/v1/chat/completions"

    def __init__(self, token: str):
        self.token = token

    def resolve(self, ru_title: str) -> str:
        prompt = (
            "Определи оригинальное англоязычное название фильма "
            f"по русскому названию: «{ru_title}». "
            "Ответь только названием фильма на английском."
        )

        headers = {
            "Authorization": f"Bearer {self.token}",
            "Content-Type": "application/json"
        }

        payload = {
            "model": "GigaChat",
            "messages": [
                {"role": "user", "content": prompt}
            ],
            "temperature": 0.2
        }

        try:
            response = requests.post(
                self.API_URL,
                headers=headers,
                json=payload,
                timeout=15
            )
            response.raise_for_status()
            result = response.json()

            return result["choices"][0]["message"]["content"].strip()

        except Exception:
            # fallback — возвращаем оригинал
            return ru_title
