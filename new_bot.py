import logging
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, WebAppInfo
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, MessageHandler, filters, ContextTypes

# ---------------- CONFIG ----------------
# 🔑 APNA TOKEN DAAL
import os
TOKEN = os.getenv("TOKEN")
VERIFY_GROUP_ID = -1003940967427

REG_LINK = "https://1weqdt.life/casino/list?open=register&p=pw1l"
PREDICTOR_URL = "https://musical-biscochitos-9846bc.netlify.app/"

# 🔥 FILE_ID IMAGES (NO BLUE ISSUE)
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
        msg = update.message.text or ""
        parts = [p.strip() for p in msg.split(":")]

        raw_id = parts[0]
        pid = "".join(filter(str.isdigit, raw_id))

        amount = float(parts[2]) if len(parts) >= 3 else 0.0

        registered_ids[pid] = amount
        print(f"✅ SYNCED: {pid} | {amount}")

    except Exception as e:
        print("SYNC ERROR:", e)

# ---------------- UI ----------------
async def show_screen(uid, context, text, keyboard, image=None):
    try:
        if uid in user_last_msg:
            await context.bot.delete_message(chat_id=uid, message_id=user_last_msg[uid])
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

        "🤖 Built on an AI-assisted system trained on extensive gameplay data and structured signal logic.\n\n"

        "📊 The model has been tested across 10,000+ game rounds and continues to improve over time.\n\n"

        "🎯 Current performance metrics indicate signal accuracy up to 95% under tracked conditions.\n\n"

        "🔐 Access is provided after completing the required setup steps below."
    )

    keyboard = [[InlineKeyboardButton("📋 Conditions", callback_data="step1")]]

    await show_screen(uid, context, text, keyboard, START_IMG)

# ---------------- STEP ----------------
async def step1(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()

    text = (
        "🌐 Step 1 — Register\n\n"

        "Register to unlock access, verification, and the next stage of the system.\n\n"

        "A new account is required so the activation process works correctly and your access can be confirmed without errors.\n\n"

        "1️⃣ If the “REGISTER” button opens an old account, log out and try again.\n\n"

        "2️⃣ Use the promo code during registration: AVAIBABA\n\n"

        "✅ After completing registration, press “CHECK REGISTRATION” to verify your account and continue."
    )

    keyboard = [
        [InlineKeyboardButton("📲 REGISTER", url=REG_LINK)],
        [InlineKeyboardButton("🔍 CHECK REGISTRATION", callback_data="ask_id")]
    ]

    await show_screen(query.from_user.id, context, text, keyboard, STEP_IMG)

# ---------------- ASK ID ----------------
async def ask_id(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.callback_query.answer("👉 Send your Player ID", show_alert=True)

# ---------------- VERIFY ----------------
async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    if update.effective_chat.type != "private":
        return

    raw = update.message.text or ""
    player_id = "".join(filter(str.isdigit, raw))

    try:
        await update.message.delete()
    except:
        pass

    await show_screen(uid, context, "⏳ Checking your deposit...\nPlease wait...", [])

    if player_id in registered_ids:
        deposit = registered_ids[player_id]

        if deposit >= 10:
            text = (
                "✅ Deposit Verified Successfully!\n\n"
                "👇 Click below to continue"
            )

            keyboard = [
                [InlineKeyboardButton("🚀 GET SIGNALS", web_app=WebAppInfo(url=PREDICTOR_URL))]
            ]

            await show_screen(uid, context, text, keyboard, SUCCESS_IMG)

        else:
            text = (
                "❌ Deposit Not Found\n\n"
                "Minimum required: 10 USDT"
            )

            keyboard = [
                [InlineKeyboardButton("💰 DEPOSIT NOW", url=REG_LINK)],
                [InlineKeyboardButton("🔁 TRY AGAIN", callback_data="ask_id")]
            ]

            await show_screen(uid, context, text, keyboard, STEP_IMG)

    else:
        text = (
            f"❌ ID {player_id} Not Found\n\n"
            "Try again after 1-2 minutes"
        )

        keyboard = [
            [InlineKeyboardButton("🔁 TRY AGAIN", callback_data="ask_id")]
        ]

        await show_screen(uid, context, text, keyboard, STEP_IMG)

# ---------------- MAIN ----------------
def main():
    app = Application.builder().token(TOKEN).build()

    app.add_handler(MessageHandler(filters.TEXT & filters.Chat(VERIFY_GROUP_ID), track_group_data))

    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(step1, pattern="step1"))
    app.add_handler(CallbackQueryHandler(ask_id, pattern="ask_id"))

    app.add_handler(MessageHandler(filters.TEXT & filters.ChatType.PRIVATE, verify))

    print("🔥 BOT RUNNING FINAL VERSION")
    app.run_polling()

if __name__ == "__main__":
    main()