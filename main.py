import os
import threading
from flask import Flask
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# এটা Render কে বোকা বানানোর জন্য, যাতে 24 ঘন্টা অন মনে করে
app_web = Flask(__name__)

@app_web.route('/')
def home():
    return "Bot is Running 24/7 for @ffpanelhub12"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# তোমার বটের কমান্ড
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("✅ বট ২৪ ঘন্টা চালু আছে ভাই!\n\n@ffpanelhub12 এর জন্য রেডি।")

async def help_cmd(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("বট অনলাইন আছে 24/7")

def main():
    # ওয়েব সার্ভার আলাদা ভাবে চালু
    threading.Thread(target=run_web).start()

    # টেলিগ্রাম বট চালু
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("help", help_cmd))
    print("24/7 Bot Started...")
    app.run_polling()

if __name__ == "__main__":
    main()
