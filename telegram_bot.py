import telegram
from telegram import Update, WebAppInfo
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import threading
from flask import Flask
import logging
import os

# Включаем логирование, чтобы видеть ошибки
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)

# --- Конфигурация ---
# Скрипт автоматически считывает эти значения из "Environment Variables" на Render
TELEGRAM_TOKEN = os.environ.get("TELEGRAM_TOKEN")
MINI_APP_URL = os.environ.get("MINI_APP_URL")


# --- Flask Web Server для "Keep-Alive" ---
# Этот мини-сервер нужен, чтобы хостинг не "усыплял" нашего бота
app = Flask(__name__)

@app.route('/')
def hello_world():
    """Эта страница будет открываться по ссылке от хостинга.
    Она нужна только для того, чтобы сервис Uptime Robot мог ее "пинговать".
    """
    return 'Bot is alive!'

def run_flask():
    """Запускает веб-сервер."""
    # 0.0.0.0 означает, что сервер будет доступен извне
    # port=10000 - стандартный порт для многих хостингов
    app.run(host='0.0.0.0', port=10000)


# --- Логика Telegram Бота ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """Отправляет приветственное сообщение с кнопкой для открытия Mini App."""
    keyboard = [
        [telegram.KeyboardButton(
            "Открыть кулинарную книгу 📖",
            web_app=WebAppInfo(url=MINI_APP_URL)
        )]
    ]
    reply_markup = telegram.ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    await update.message.reply_text(
        "Добро пожаловать в кулинарную книгу! Нажмите кнопку ниже, чтобы открыть каталог рецептов.",
        reply_markup=reply_markup
    )


# --- Основное выполнение ---
if __name__ == '__main__':
    # Проверяем, что переменные окружения были успешно загружены
    if not TELEGRAM_TOKEN or not MINI_APP_URL:
        print("!!! ОШИБКА: Переменные окружения TELEGRAM_TOKEN и MINI_APP_URL не установлены на хостинге! !!!")
        print("!!! Пожалуйста, проверьте настройки 'Environment' вашего сервиса на Render.com !!!")
    else:
        # Запускаем Flask в отдельном потоке, чтобы он не блокировал бота
        flask_thread = threading.Thread(target=run_flask)
        flask_thread.start()

        # Создаем и запускаем Telegram бота
        application = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
        application.add_handler(CommandHandler("start", start))

        print("Бот запущен и готов к работе...")
        application.run_polling()

