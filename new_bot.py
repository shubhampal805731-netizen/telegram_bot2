import asyncio
import os
import threading
from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    ContextTypes,
    filters,
)

# ---------------- CONFIG ----------------
TOKEN = os.getenv("TOKEN")
VERIFY_GROUP_ID = -1003940967427

REG_LINK = "https://1weqdt.life/casino/list?open=register&p=pw1l"
PREDICTOR_URL = "https://musical-biscochitos-9846bc.netlify.app/"

if not TOKEN:
    print("❌ TOKEN NOT FOUND")
    raise SystemExit(1)

# ---------------- FLASK (PORT KEEP-ALIVE) ----------------
app_flask = Flask(__name__)

@app_flask.route("/")
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host="0.0.0.0", port=port)

# ---------------- STORAGE ----------------
registered_ids = {}

# ---------------- HANDLERS ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [[InlineKeyboardButton("📋 Conditions", callback_data="step1")]]
    await update.message.reply_text(
        "🎰 Welcome to Jetphile AI Bot",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def step1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    keyboard = [
        [InlineKeyboardButton("📲 REGISTER", url=REG_LINK)],
        [InlineKeyboardButton("🔍 CHECK REGISTRATION", callback_data="ask_id")],
    ]

    await q.message.reply_text(
        "Register first and then verify your ID",
        reply_markup=InlineKeyboardMarkup(keyboard),
    )

async def ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Send your Player ID", show_alert=True)

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ Bot working perfectly")

# ---------------- MAIN ----------------
async def main():
    app = Application.builder().token(TOKEN).build()

    # handlers
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(step1, pattern="step1"))
    app.add_handler(CallbackQueryHandler(ask_id, pattern="ask_id"))
    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, verify))

    print("🔥 BOT STARTED")

    # flask server (Render free fix)
    threading.Thread(target=run_web, daemon=True).start()

    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)

    print("🚀 POLLING STARTED")

    await app.run_polling()

if __name__ == "__main__":
    asyncio.run(main())
