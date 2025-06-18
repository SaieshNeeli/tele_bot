import logging
import httpx
import asyncio
import nest_asyncio
import os
from telegram import Update
from telegram.ext import ApplicationBuilder, ContextTypes, MessageHandler, filters

# === Tokens (read from environment) ===
TELEGRAM_BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
OPENROUTER_API_KEY = os.getenv("OPENROUTER_API_KEY")
#BOT_USERNAME = os.getenv("BOT_USERNAME", "your_bot_username")  # Optional fallback

# === Function to call OpenRouter ===
async def get_openrouter_reply(user_message):
    headers = {
        "Authorization": f"Bearer {OPENROUTER_API_KEY}",
        "HTTP-Referer": f"https://t.me/@last_message_reply_bot",
        "X-Title": "Telegram Chatbot",
        "Content-Type": "application/json"
    }

    data = {
        "model": "mistralai/mistral-7b-instruct",
        "messages": [
            {"role": "system", "content": "You are a chill, funny BTech student who replies in Tenglish."},
            {"role": "user", "content": user_message}
        ]
    }

    try:
        async with httpx.AsyncClient() as client:
            response = await client.post("https://openrouter.ai/api/v1/chat/completions", headers=headers, json=data)
            response.raise_for_status()
            result = response.json()
            return result["choices"][0]["message"]["content"].strip()
    except Exception as e:
        return f"Error: {str(e)}"

# === Telegram Handler ===
async def reply_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text
    reply = await get_openrouter_reply(user_message)
    await update.message.reply_text(reply)

# === Bot main ===
async def main():
    app = ApplicationBuilder().token(TELEGRAM_BOT_TOKEN).build()
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, reply_handler))
    print("🤖 Telegram bot is running...")
    await app.run_polling()

# === Start the bot ===
nest_asyncio.apply()
asyncio.run(main())
