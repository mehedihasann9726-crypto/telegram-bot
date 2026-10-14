import os
import asyncio
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

# তোমার বটের ডাটা এখানে থাকবে (Render এর মেমোরিতে)
users = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    args = context.args

    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "referred_by": None}

        # রেফার চেক
        if args and len(args) > 0:
            try:
                referrer_id = int(args[0])
                if referrer_id!= user_id and referrer_id in users:
                    users[referrer_id]["balance"] += 2
                    users[referrer_id]["referrals"] += 1
                    users[user_id]["referred_by"] = referrer_id
                    await context.bot.send_message(
                        chat_id=referrer_id,
                        text=f"🎉 অভিনন্দন! আপনার রেফারে একজন জয়েন করেছে। আপনি 2 টাকা পেয়েছেন!"
                    )
            except:
                pass

    bal = users[user_id]["balance"]
    ref = users[user_id]["referrals"]
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user_id}"

    text = f"""
👋 স্বাগতম!

💰 আপনার ব্যালেন্স: {bal} টাকা
👥 আপনার রেফার: {ref} জন

🔗 আপনার রেফার লিঙ্ক:
{link}

প্রতি রেফারে 2 টাকা! 25 টাকা হলেই উইথড্র করতে পারবেন।

কমান্ড:
 /balance - ব্যালেন্স দেখুন
 /refer - রেফার লিঙ্ক
 /withdraw - উইথড্র
"""
    await update.message.reply_text(text)

async def balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "referred_by": None}
    await update.message.reply_text(f"💰 আপনার ব্যালেন্স: {users[user_id]['balance']} টাকা\n👥 রেফার: {users[user_id]['referrals']} জন")

async def refer(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    bot_username = (await context.bot.get_me()).username
    link = f"https://t.me/{bot_username}?start={user_id}"
    await update.message.reply_text(f"🔗 আপনার রেফার লিঙ্ক:\n{link}\n\nপ্রতি রেফারে 2 টাকা!")

async def withdraw(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.effective_user.id
    if user_id not in users:
        users[user_id] = {"balance": 0, "referrals": 0, "referred_by": None}

    bal = users[user_id]["balance"]
    if bal < 25:
        await update.message.reply_text(f"❌ উইথড্র করতে 25 টাকা লাগবে। আপনার আছে {bal} টাকা। আরও {25-bal} টাকা লাগবে।")
    else:
        await update.message.reply_text(f"✅ উইথড্র রিকোয়েস্ট পেয়েছি! {bal} টাকা।\n\nএডমিন শীঘ্রই পেমেন্ট করে দিবে। @admin এর সাথে যোগাযোগ করুন।")
        users[user_id]["balance"] = 0

def main():
    if not TOKEN:
        print("ERROR: TELEGRAM_BOT_TOKEN not found!")
        return
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("balance", balance))
    app.add_handler(CommandHandler("refer", refer))
    app.add_handler(CommandHandler("withdraw", withdraw))
    print("Bot is running...")
    app.run_polling()

if __name__ == "__main__":
    main()
