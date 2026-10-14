import os, json
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, CallbackQueryHandler, filters, ContextTypes

TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")
CHANNEL_1_USERNAME = "ffpanelhub12"
CHANNEL_1_DISPLAY = "💳 Payment Channel"
CHANNEL_2_USERNAME = "ref2refgroup1"
CHANNEL_2_DISPLAY = "📢 Main Channel"
PER_REFER = 2
MIN_WITHDRAW = 25
DATA_FILE = "users.json"

def load_users():
    if os.path.exists(DATA_FILE):
        try:
            with open(DATA_FILE, "r") as f: return json.load(f)
        except: return {}
    return {}
def save_users(u):
    with open(DATA_FILE, "w") as f: json.dump(u, f)
users = load_users()

def main_kb():
    return ReplyKeyboardMarkup([["💰 Balance","👤 প্রোফাইল"],["👥 My Refer Link","📊 Total Users"],["🔴 Withdraw","🚀 Start"]], resize_keyboard=True)
def join_kb():
    return InlineKeyboardMarkup([[InlineKeyboardButton(CHANNEL_1_DISPLAY, url=f"https://t.me/{CHANNEL_1_USERNAME}")],[InlineKeyboardButton(CHANNEL_2_DISPLAY, url=f"https://t.me/{CHANNEL_2_USERNAME}")],[InlineKeyboardButton("✅ Verify", callback_data="verify")]])

async def is_joined(uid, bot):
    try:
        m1 = await bot.get_chat_member(f"@{CHANNEL_1_USERNAME}", uid)
        m2 = await bot.get_chat_member(f"@{CHANNEL_2_USERNAME}", uid)
        ok = ['member','administrator','creator']
        return m1.status in ok and m2.status in ok
    except: return False

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    name = update.effective_user.first_name
    if uid not in users:
        users[uid] = {"name": name, "balance": 0, "ref_count": 0}
        if context.args and context.args[0].startswith("ref"):
            ref = context.args[0][3:]
            if ref!= uid and ref in users:
                users[ref]["balance"] += PER_REFER
                users[ref]["ref_count"] += 1
                try: await context.bot.send_message(int(ref), f"🎉 নতুন রেফার! {name} জয়েন করেছে। +{PER_REFER} টাকা!")
                except: pass
        save_users(users)
    if not await is_joined(update.effective_user.id, context.bot):
        await update.message.reply_text(f"👋 হ্যালো {name}!\n\n🤖 বট ব্যবহার করতে 2 টা চ্যানেলে Join করো 👇\n\n💰 প্রতি রেফারে {PER_REFER} টাকা\n💸 মিনিমাম উইথড্র {MIN_WITHDRAW} টাকা", reply_markup=join_kb())
        return
    await update.message.reply_text(f"✅ ভেরিফাই সফল {name}!\n\n💰 ব্যালেন্স: {users[uid]['balance']} টাকা\n👥 রেফার: {users[uid]['ref_count']} জন", reply_markup=main_kb())

async def verify(update: Update, context: ContextTypes.DEFAULT_TYPE):
    q = update.callback_query
    await q.answer()
    uid = str(q.from_user.id)
    if await is_joined(q.from_user.id, context.bot):
        await q.message.delete()
        await context.bot.send_message(q.from_user.id, f"✅ ভেরিফাইড!\n💰 ব্যালেন্স: {users[uid]['balance']} টাকা", reply_markup=main_kb())
    else:
        await q.answer("❌ এখনো 2 টা চ্যানেলে জয়েন করো নাই!", show_alert=True)

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = str(update.effective_user.id)
    text = update.message.text or ""
    if not await is_joined(update.effective_user.id, context.bot):
        await update.message.reply_text("⚠️ আগে 2 টা চ্যানেলে Join করে Verify করো 👇", reply_markup=join_kb())
        return
    if uid not in users:
        users[uid] = {"name": update.effective_user.first_name, "balance": 0, "ref_count": 0}
        save_users(users)
    me = await context.bot.get_me()
    if "Balance" in text or "Start" in text:
        await update.message.reply_text(f"💰 ব্যালেন্স: {users[uid]['balance']} টাকা", reply_markup=main_kb())
    elif "প্রোফাইল" in text:
        u = users[uid]
        await update.message.reply_text(f"👤 প্রোফাইল\n\n🙎‍♂️ নাম: {u['name']}\n🆔 ID: {uid}\n💰 ব্যালেন্স: {u['balance']} টাকা\n👥 মোট রেফার: {u['ref_count']} জন", reply_markup=main_kb())
    elif "Refer" in text:
        u = users[uid]
        await update.message.reply_text(f"👥 তোমার রেফার লিংক:\nhttps://t.me/{me.username}?start=ref{uid}\n\nরেফার করেছো: {u['ref_count']} জন\nপ্রতি রেফারে {PER_REFER} টাকা", reply_markup=main_kb())
    elif "Total" in text:
        await update.message.reply_text(f"📊 মোট ইউজার: {len(users)} জন", reply_markup=main_kb())
    elif "Withdraw" in text:
        bal = users[uid]['balance']
        if bal < MIN_WITHDRAW:
            await update.message.reply_text(f"🔴 উইথড্র করতে {MIN_WITHDRAW} টাকা লাগবে। আছে {bal} টাকা।", reply_markup=main_kb())
        else:
            await update.message.reply_text(f"✅ {bal} টাকা উইথড্র রিকোয়েস্ট নেওয়া হয়েছে!", reply_markup=main_kb())
            users[uid]['balance'] = 0
            save_users(users)

if __name__ == "__main__":
    app = ApplicationBuilder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CallbackQueryHandler(verify, pattern="verify"))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle))
    app.run_polling()
