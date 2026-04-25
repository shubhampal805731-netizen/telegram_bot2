import asyncio
import os
import threading
from flask import Flask

from telegram import Update
from telegram.ext import Application, CommandHandler

# ---------------- CONFIG ----------------
TOKEN = os.getenv("TOKEN")

print("TOKEN VALUE:", TOKEN)

if not TOKEN:
    print("❌ TOKEN NOT FOUND")
    exit()

# ---------------- FLASK ----------------
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

# ---------------- BOT ----------------
async def start(update: Update, context):
    await update.message.reply_text("🔥 Bot chal raha hai")

# ---------------- MAIN ----------------
async def main():
    try:
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))

        print("🔥 BOT STARTED")

        threading.Thread(target=run_web, daemon=True).start()

        await app.initialize()
        await app.start()
        await app.bot.delete_webhook(drop_pending_updates=True)

        print("🚀 POLLING STARTED")

        await app.run_polling()

    except Exception as e:
        print("❌ FULL ERROR:", e)

if __name__ == "__main__":
    asyncio.run(main())
