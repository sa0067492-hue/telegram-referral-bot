import os
import sqlite3
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

TOKEN = os.getenv("BOT_TOKEN")

POINT_PER_REF = 10

db = sqlite3.connect("users.db", check_same_thread=False)
cur = db.cursor()

cur.execute("""
CREATE TABLE IF NOT EXISTS users(
id INTEGER PRIMARY KEY,
points INTEGER DEFAULT 0,
ref INTEGER DEFAULT 0
)
""")
db.commit()


async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user = update.effective_user
    uid = user.id

    cur.execute("SELECT id FROM users WHERE id=?", (uid,))
    if not cur.fetchone():
        cur.execute("INSERT INTO users(id) VALUES(?)", (uid,))
        db.commit()

        if context.args:
            try:
                ref = int(context.args[0])
                if ref != uid:
                    cur.execute(
                        "UPDATE users SET points=points+?, ref=ref+1 WHERE id=?",
                        (POINT_PER_REF, ref)
                    )
                    db.commit()
            except:
                pass

    link = f"https://t.me/{context.bot.username}?start={uid}"

    await update.message.reply_text(
        f"👋 Welcome {user.first_name}\n\n"
        f"🔗 Your Referral Link:\n{link}\n\n"
        f"🎁 Invite friends and get {POINT_PER_REF} points per user."
    )


async def points(update: Update, context: ContextTypes.DEFAULT_TYPE):
    uid = update.effective_user.id

    cur.execute("SELECT points,ref FROM users WHERE id=?", (uid,))
    data = cur.fetchone()

    if data:
        await update.message.reply_text(
            f"⭐ Points: {data[0]}\n"
            f"👥 Referrals: {data[1]}"
        )
    else:
        await update.message.reply_text("Use /start first")


app = Application.builder().token(TOKEN).build()

app.add_handler(CommandHandler("start", start))
app.add_handler(CommandHandler("points", points))

app.run_polling()
