import os
from flask import Flask, request
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters

TOKEN = os.getenv("TOKEN")
APP_URL = os.getenv("RENDER_EXTERNAL_URL")  # Render खुद देता है

if not TOKEN:
    print("❌ TOKEN NOT FOUND")
    raise SystemExit(1)

app = Flask(__name__)
bot_app = Application.builder().token(TOKEN).build()

# -------- HANDLERS --------
async def start(update, context):
    keyboard = [[InlineKeyboardButton("📋 Conditions", callback_data="step1")]]
    await update.message.reply_text(
        "🎰 Bot chal raha hai",
        reply_markup=InlineKeyboardMarkup(keyboard)
    )

async def step1(update, context):
    q = update.callback_query
    await q.answer()
    await q.message.reply_text("Step 1 complete")

async def verify(update, context):
    await update.message.reply_text("✅ Working")

bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CallbackQueryHandler(step1, pattern="step1"))
bot_app.add_handler(MessageHandler(filters.TEXT, verify))

# -------- FLASK ROUTES --------
@app.route("/")
def home():
    return "Bot is running"

@app.route(f"/{TOKEN}", methods=["POST"])
def webhook():
    update = Update.de_json(request.get_json(force=True), bot_app.bot)
    bot_app.update_queue.put_nowait(update)
    return "ok"

# -------- START --------
if __name__ == "__main__":
    import asyncio

    async def init():
        await bot_app.initialize()
        await bot_app.bot.set_webhook(f"{APP_URL}/{TOKEN}")
        print("🚀 WEBHOOK SET:", f"{APP_URL}/{TOKEN}")

    asyncio.run(init())

    port = int(os.environ.get("PORT", 10000))
    app.run(host="0.0.0.0", port=port)
