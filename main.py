import telebot
from flask import Flask, request
import sqlite3
import os

TOKEN = "6386667633:AAFjQC83NCgrsq1WXPWxgWZfoYTVytzQ3XI"  # Ваш токен Telegram
WEBHOOK_URL = "https://bottest-4736.onrender.com/webhook/telegram"  # Используйте ваш URL

bot = telebot.TeleBot(TOKEN)

app = Flask(__name__)

# Подключение к базе данных SQLite
conn = sqlite3.connect('subscribers.db', check_same_thread=False)
cursor = conn.cursor()

# Создание таблицы для хранения подписчиков
cursor.execute('''
CREATE TABLE IF NOT EXISTS subscribers (
    user_id INTEGER PRIMARY KEY
)
''')
conn.commit()

# Функция для проверки новых подписчиков
def check_new_subscriber(user_id):
    cursor.execute('SELECT user_id FROM subscribers WHERE user_id = ?', (user_id,))
    return cursor.fetchone() is None

# Функция для добавления нового подписчика в базу данных
def add_subscriber(user_id):
    cursor.execute('INSERT INTO subscribers (user_id) VALUES (?)', (user_id,))
    conn.commit()

# Обработчик webhook
@app.route('/webhook/telegram', methods=['POST'])
def webhook():
    try:
        json_str = request.get_data().decode('UTF-8')
        update = telebot.types.Update.de_json(json_str)
        bot.process_new_updates([update])
    except Exception as e:
        print(f"Ошибка обработки webhook: {e}")
    return 'ok', 200

# Обработчик новых сообщений
@bot.message_handler(content_types=['new_chat_members'])
def handle_new_member(message):
    try:
        for member in message.new_chat_members:
            user_id = member.id
            if check_new_subscriber(user_id):
                add_subscriber(user_id)
                bot.send_message(user_id, "Добро пожаловать в наш канал!")
    except Exception as e:
        print(f"Ошибка обработки новых участников: {e}")

# Установка вебхука
bot.remove_webhook()
bot.set_webhook(url=WEBHOOK_URL)

# Запуск Flask-сервера (только для локальной отладки)
if __name__ == '__main__':
    app.run(host='0.0.0.0', port=5000)
