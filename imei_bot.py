import telebot
import requests
import re
import os


TOKEN = os.getenv("TOKEN")
API_BACKEND_URL = "http://127.0.0.1:8000/api/check-imei"
API_AUTH_TOKEN = ""  # Введите ваш access-токен

bot = telebot.TeleBot(TOKEN)

ALLOWED_USERS = [1499956633]


@bot.message_handler(commands=["start"])
def send_welcome(message):
    user_id = message.from_user.id

    if user_id not in ALLOWED_USERS:
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return

    bot.reply_to(
        message,
        (f"Привет! Отправьте IMEI (15 цифр), и я найду информацию. "
         f"Ваш UserId: {user_id}")
    )


@bot.message_handler(func=lambda message: True)
def handle_message(message):
    if message.from_user.id not in ALLOWED_USERS:
        bot.reply_to(message, "Извините, у вас нет доступа к этому боту.")
        return

    imei = message.text.strip()
    if not re.fullmatch(r"\d{15}", imei):
        bot.reply_to(message, "Неверный формат IMEI. Должно быть 15 цифр.")
        return

    headers = {
        "Content-Type": "application/json",
        "Authorization": f"Bearer {API_AUTH_TOKEN}"
    }
    payload = {"imei": imei, "token": API_AUTH_TOKEN}

    try:
        response = requests.post(
            API_BACKEND_URL,
            json=payload,
            headers=headers,
            timeout=10
        )

        if response.status_code != 200:
            bot.reply_to(
                message,
                f"Ошибка API ({response.status_code}): {response.text}")
            return

        data = response.json()

        if "error" in data:
            bot.reply_to(message, f"Ошибка: {data['error']}")
            return

        result_text = format_response(data)
        bot.reply_to(message, result_text)

    except requests.RequestException as e:
        bot.reply_to(message, f"Ошибка соединения с API: {str(e)}")


def format_response(data):
    """Форматирует ответ API в удобочитаемый вид."""
    if not isinstance(data, dict):
        return str(data)

    output = "📡 Информация об устройстве:\n"
    for key, value in data.items():
        output += f"🔹 {key}: {value}\n"
    return output


if __name__ == "__main__":
    print("Бот запущен...")
    bot.polling(none_stop=True)
