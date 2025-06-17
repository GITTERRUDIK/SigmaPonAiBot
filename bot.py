import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes

from llama_index.llms.openai import OpenAI
from llama_index import VectorStoreIndex, SimpleDirectoryReader, ServiceContext

# === Настройка LLM через OpenRouter ===
llm = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="deepseek-coder:6.7b",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.4,
    system_prompt=(
        "Ты — личный помощник Шмоти (aka pakkva, smilejany). Пиши кратко, спокойно, понятным языком, говори на 'ты'. "
        "Если тебя просят сгенерировать код — пиши чисто, понятно, без мусора и лишних комментариев"
        "Ты умеешь писать на Python, HTML, JS и LuaU."
        "Не сюсюкайся, не говори как ты выражаешь сочуствие. В основном ты только нацелен на генерацию кода, обьяснение непонятных тем. И иногда небольшие разговоры"
    )
)

# === Ответ бота на входящее сообщение ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    response = query_engine.query(user_input)
    await update.message.reply_text(str(response))

# === Основная точка входа ===
def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    if not TELEGRAM_TOKEN:
        print("⛔ Укажи TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY в переменных окружения")
        return

    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
