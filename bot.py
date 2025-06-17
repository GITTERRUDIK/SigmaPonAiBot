import os
from telegram import Update
from telegram.ext import ApplicationBuilder, MessageHandler, filters, ContextTypes
from llama_index.llms.openai import OpenAI

# === Настройка LLM через OpenRouter ===
llm = OpenAI(
    api_key=os.getenv("OPENROUTER_API_KEY"),
    model="deepseek-coder:6.7b",
    base_url="https://openrouter.ai/api/v1",
    temperature=0.4,
    system_prompt=(
        "Ты — личный помощник Шмоти (aka pakkva, smilejany). Пиши кратко, спокойно, понятным языком, говори на 'ты'. "
        "Если тебя просят сгенерировать код — пиши чисто, понятно, без мусора и лишних комментариев "
        "Ты умеешь писать на Python, HTML, JS и LuaU. "
        "Не сюсюкайся, не говори как ты выражаешь сочуствие. В основном ты только нацелен на генерацию кода, обьяснение непонятных тем. И иногда небольшие разговоры"
    )
)

# === Ответ бота на входящее сообщение ===
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_input = update.message.text
    
    try:
        # Прямой запрос к LLM без векторного индекса
        response = await llm.acomplete(user_input)
        await update.message.reply_text(str(response))
    except Exception as e:
        print(f"Ошибка при обработке сообщения: {e}")
        await update.message.reply_text("Произошла ошибка при обработке запроса")

# === Основная точка входа ===
def main():
    TELEGRAM_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
    OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
    
    if not TELEGRAM_TOKEN or not OPENROUTER_API_KEY:
        print("⛔ Укажи TELEGRAM_BOT_TOKEN и OPENROUTER_API_KEY в переменных окружения")
        return
    
    app = ApplicationBuilder().token(TELEGRAM_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))
    
    print("✅ Бот запущен!")
    app.run_polling()

if __name__ == "__main__":
    main()
