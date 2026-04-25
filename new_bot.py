import logging
import asyncio
import os
import threading
from flask import Flask

from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------- CONFIG ----------------
TOKEN = os.getenv("TOKEN")

if not TOKEN:
    print("❌ TOKEN NOT FOUND - CHECK ENV VARIABLE")
    exit()

VERIFY_GROUP_ID = -1003940967427

REG_LINK = "https://1weqdt.life/casino/list?open=register&p=pw1l"
PREDICTOR_URL = "https://musical-biscochitos-9846bc.netlify.app/"

# ---------------- FLASK ----------------
app_flask = Flask(__name__)

@app_flask.route('/')
def home():
    return "Bot is running"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_flask.run(host='0.0.0.0', port=port)

# ---------------- IMAGES ----------------
START_IMG = "AgACAgUAAxkBAAIBImnq0Z281-_HI1LQtxbDGjTDBGD3AAIOEWsbba5ZV2C2xSmH7R4AAQEAAwIAA3kAAzsE"
STEP_IMG = "AgACAgUAAxkBAAIBKGnq0f8n8kgsRF0dakH9NaNwSJPRAAIQEWsbba5ZV9WqVW_bSC8uAQADAgADeQADOwQ"
SUCCESS_IMG = "AgACAgUAAxkBAAIBJGnq0adOwepZKar859UrgSkm6Dd-AAIPEWsbba5ZV9J092-Ij5Q2AQADAgADeQADOwQ"

# ---------------- STORAGE ----------------
registered_ids = {}
user_last_msg = {}

# ---------------- GROUP SYNC ----------------
async def track_group_data(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or update.effective_chat.id != VERIFY_GROUP_ID:
        return
    try:
        parts = [p.strip() for p in (update.message.text or "").split(":")]
        pid = "".join(filter(str.isdigit, parts[0]))
        amount = float(parts[2]) if len(parts) >= 3 else 0.0
        registered_ids[pid] = amount
    except:
        pass

# ---------------- UI ----------------
async def show_screen(uid, context, text, keyboard, image=None):
    try:
        if uid in user_last_msg:
            await context.bot.delete_message(uid, user_last_msg[uid])
    except:
        pass

    if image:
        msg = await context.bot.send_photo(
            chat_id=uid,
            photo=image,
            caption=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )
    else:
        msg = await context.bot.send_message(
            chat_id=uid,
            text=text,
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode="Markdown"
        )

    user_last_msg[uid] = msg.message_id

# ---------------- START ----------------
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    text = (
        "🎰 Welcome to Jetphile AI Bot.\n\n"
        "🤖 AI-based system trained on gameplay data.\n\n"
        "📊 Tested on 10,000+ rounds.\n\n"
        "🎯 Accuracy up to 95%.\n\n"
        "🔐 Complete steps to unlock access."
    )

    keyboard = [[InlineKeyboardButton("📋 Conditions", callback_data="step1")]]

    await show_screen(uid, context, text, keyboard, START_IMG)

# ---------------- STEP ----------------
async def step1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()

    text = (
        "🌐 Step 1 — Register\n\n"
        "Create a new account\n\n"
        "Use promo: AVAIBABA\n\n"
        "Then click CHECK REGISTRATION"
    )

    keyboard = [
        [InlineKeyboardButton("📲 REGISTER", url=REG_LINK)],
        [InlineKeyboardButton("🔍 CHECK REGISTRATION", callback_data="ask_id")]
    ]

    await show_screen(q.from_user.id, context, text, keyboard, STEP_IMG)

# ---------------- ASK ID ----------------
async def ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("Send Player ID", show_alert=True)

# ---------------- VERIFY ----------------
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if update.effective_chat.type != "private":
        return

    pid = "".join(filter(str.isdigit, update.message.text or ""))

    await show_screen(uid, context, "⏳ Checking deposit...", [])

    if pid in registered_ids and registered_ids[pid] >= 10:
        keyboard = [[InlineKeyboardButton("🚀 GET SIGNALS", web_app=WebAppInfo(url=PREDICTOR_URL))]]
        await show_screen(uid, context, "✅ Verified", keyboard, SUCCESS_IMG)
    else:
        keyboard = [[InlineKeyboardButton("🔁 Retry", callback_data="ask_id")]]
        await show_screen(uid, context, "❌ Not found", keyboard, STEP_IMG)

# ---------------- MAIN ----------------
async def main():
    try:
        app = Application.builder().token(TOKEN).build()

        app.add_handler(CommandHandler("start", start))
        app.add_handler(CallbackQueryHandler(step1, pattern="step1"))
        app.add_handler(CallbackQueryHandler(ask_id, pattern="ask_id"))
        app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, verify))
        app.add_handler(MessageHandler(filters.TEXT & filters.Chat(VERIFY_GROUP_ID), track_group_data))

        print("🔥 BOT STARTED")

        threading.Thread(target=run_web, daemon=True).start()

        await app.initialize()
        await app.start()
        await app.bot.delete_webhook(drop_pending_updates=True)

        print("🚀 POLLING STARTED")

        await app.run_polling()

    except Exception as e:
        print("❌ FULL ERROR:", e)
    # Flask thread
    threading.Thread(target=run_web, daemon=True).start()

    await app.initialize()
    await app.start()
    await app.bot.delete_webhook(drop_pending_updates=True)

    print("🚀 POLLING STARTED")

    # ✅ FIXED LINE
    await app.run_polling(close_loop=False)

if __name__ == "__main__":
    asyncio.run(main())
