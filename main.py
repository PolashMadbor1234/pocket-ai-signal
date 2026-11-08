import os
import logging
from telegram import InlineKeyboardButton, InlineKeyboardMarkup, Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

logging.basicConfig(
    format="%(asctime)s %(levelname)s %(name)s: %(message)s",
    level=logging.INFO,
)
log = logging.getLogger("polash-pro")

BROKERS = {"quotex": "Quotex", "pocket": "Pocket Option"}
MARKETS = {"otc": "OTC", "real": "Real Market"}
EXPIRIES = {"5s": "৫ সেকেন্ড", "15s": "১৫ সেকেন্ড", "30s": "৩০ সেকেন্ড", "1m": "১ মিনিট"}


def menu():
    return InlineKeyboardMarkup([
        [
            InlineKeyboardButton("Quotex", callback_data="broker:quotex"),
            InlineKeyboardButton("Pocket Option", callback_data="broker:pocket"),
        ],
        [
            InlineKeyboardButton("📊 Real Market", callback_data="market:real"),
            InlineKeyboardButton("🟣 OTC Market", callback_data="market:otc"),
        ],
        [
            InlineKeyboardButton("⏱ ৫ সেকেন্ড", callback_data="expiry:5s"),
            InlineKeyboardButton("⏱ ১৫ সেকেন্ড", callback_data="expiry:15s"),
        ],
        [
            InlineKeyboardButton("⏱ ৩০ সেকেন্ড", callback_data="expiry:30s"),
            InlineKeyboardButton("⏱ ১ মিনিট", callback_data="expiry:1m"),
        ],
        [InlineKeyboardButton("🔎 সিগন্যালের অবস্থা", callback_data="signal")],
    ])


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    context.user_data.setdefault("broker", "quotex")
    context.user_data.setdefault("market", "real")
    context.user_data.setdefault("expiry", "1m")
    await update.message.reply_text(
        "স্বাগতম! এটি Polash Pro Trading Bot।\n\n"
        "Broker, Market ও Expiry নির্বাচন করুন।\n"
        "বিশ্লেষণ সেটিংস: Trend 1H | EMA 50/200 | RSI threshold 52 | Momentum period 4",
        reply_markup=menu(),
    )


async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "/start — বট চালু করুন\n"
        "/settings — নির্বাচন মেনু দেখুন\n"
        "/help — সাহায্য\n\n"
        "সতর্কতা: কোনো সিগন্যাল লাভ নিশ্চিত করে না।"
    )


async def settings(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        "আপনার ট্রেডিং সেটিংস নির্বাচন করুন:",
        reply_markup=menu(),
    )


async def button_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    query = update.callback_query
    await query.answer()
    data = query.data

    if data.startswith("broker:"):
        context.user_data["broker"] = data.split(":", 1)[1]
        await query.edit_message_text(
            f"প্ল্যাটফর্ম: {BROKERS[context.user_data['broker']]}\n"
            "এখন Market ও Expiry বেছে নিন:",
            reply_markup=menu(),
        )
    elif data.startswith("market:"):
        context.user_data["market"] = data.split(":", 1)[1]
        await query.edit_message_text(
            f"Market: {MARKETS[context.user_data['market']]}\n"
            "এখন Expiry ও বিশ্লেষণের অবস্থা দেখুন:",
            reply_markup=menu(),
        )
    elif data.startswith("expiry:"):
        context.user_data["expiry"] = data.split(":", 1)[1]
        await query.edit_message_text(
            f"Expiry: {EXPIRIES[context.user_data['expiry']]}\n"
            "সেটিংস নির্বাচিত হয়েছে।",
            reply_markup=menu(),
        )
    elif data == "signal":
        broker = BROKERS.get(context.user_data.get("broker", "quotex"), "Quotex")
        market = MARKETS.get(context.user_data.get("market", "real"), "Real Market")
        expiry = EXPIRIES.get(context.user_data.get("expiry", "1m"), "১ মিনিট")
        await query.edit_message_text(
            "📡 Polash Pro — বিশ্লেষণের অবস্থা\n\n"
            f"প্ল্যাটফর্ম: {broker}\n"
            f"Market: {market}\n"
            f"Expiry: {expiry}\n\n"
            "⚠️ WAIT — এখনো যাচাইকৃত লাইভ OHLC ডেটা ফিড সংযুক্ত নেই।\n"
            "ডেটা ছাড়া CALL/PUT তৈরি করা হবে না।\n\n"
            "প্রোফাইল: Trend 1H, EMA 50/200, RSI threshold 52, Momentum period 4।",
            reply_markup=menu(),
        )


def main():
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        raise RuntimeError(
            "TELEGRAM_BOT_TOKEN সেট করা নেই। Hosting-এর Environment Variables-এ Token দিন।"
        )

    app = Application.builder().token(token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_command))
    app.add_handler(CommandHandler("settings", settings))
    app.add_handler(CallbackQueryHandler(button_handler))
    log.info("Polash Pro bot is starting.")
    app.run_polling()


if __name__ == "__main__":
    main()
