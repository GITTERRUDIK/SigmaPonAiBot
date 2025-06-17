import os
import logging
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes
from llama_index.llms.openai import OpenAI
from flask import Flask, request
import asyncio
import threading

# Настройка логирования
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# === Flask приложение для Render ===
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

@app.route('/health')
def health():
    return "OK", 200

# === Настройка LLM через OpenRouter ===
llm = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="deepseek/deepseek-coder",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.4
)

# === Ответ бота на входящее сообщение ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    logger.info(f"Получено сообщение: {user_input}")
    
    # Добавляем системный промпт к сообщению пользователя
    full_prompt = f"""Ты — личный помощник Шмоти (aka pakkva, smilejany). Пиши кратко, спокойно, понятным языком, говори на 'ты'. 
Если тебя просят сгенерировать код — пиши чисто, понятно, без мусора и лишних комментариев.
Ты умеешь писать на Python, HTML, JS и LuaU.
Не сюсюкайся, не говори как ты выражаешь сочуствие. В основном ты только нацелен на генерацию кода, обьяснение непонятных тем. И иногда небольшие разговоры.

Вопрос пользователя: {user_input}"""
    
    try:
        logger.info("Отправляем запрос к LLM...")
        response = await llm.acomplete(full_prompt)
        logger.info(f"Получен ответ от LLM: {str(response)[:100]}...")
        await update.message.reply_text(str(response))
    except Exception as e:
        logger.error(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса")

# === Запуск бота в отдельном потоке ===
def run_bot():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        logger.error("⛔ Укажи TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY в переменных окружения")
        return
    
    bot_app = Application.builder().token(TELEGRAM_TOKEN).build()
    bot_app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    logger.info("✅ Бот запущен!")
    bot_app.run_polling(drop_pending_updates=True)

# === Основная точка входа ===
if __name__ == "__main__":
    # Запускаем бота в отдельном потоке
    bot_thread = threading.Thread(target=run_bot, daemon=True)
    bot_thread.start()
    
    # Запускаем Flask сервер для Render
    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port, debug=False)
