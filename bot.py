import os
import requests
import sqlite3
from flask import Flask, request
from threading import Thread
from telegram import Update
from telegram.ext import Application, CommandHandler, ContextTypes

app = Flask(__name__)

DB_FILE = "subs.db"

def init_db():
    conn = sqlite3.connect(DB_FILE)
    c = conn.cursor()
    c.execute("CREATE TABLE IF NOT EXISTS subs (uid TEXT, chat_id TEXT)")
    conn.commit()
    conn.close()

init_db()

# 🔥 LƯU Ý: Dùng trực tiếp string, KHÔNG dùng os.getenv()
TOKEN = "7618142601:AAH4_zzpHyy7wjioC9QbBCtXcuNO-roKl8s"
FB_TOKEN = "EAAGNO4a7r2wBPyLgahrnYRBnA4qQKZAlY5aofyumyBqHRhPZCwOzCSevSOiaaGpWCxZABbm9OMeYMghSZA4q3KPfnmcw396tQPGI9cTZAqF9feQn33HJtjj4QqGa3ZCiD7EXZCGZCgxbwPpWFvLCywzZCY74Gd9Aa8xOoWkphBvZAUFrUsap7GrcnOoOjfsWmYSHCJtwZDZD"
GRAPH_VERSION = "v19.0"

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Gửi /check <uid> để kiểm tra live.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Vui lòng nhập UID\nVí dụ: /check 123456789")
        return

    uid = context.args[0]
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{uid}/live_videos"

    r = requests.get(url, params={"access_token": FB_TOKEN})

    if r.status_code != 200:
        await update.message.reply_text("⚠️ Lỗi token FB hoặc UID sai!")
        return

    data = r.json().get("data", [])
    if data:
        await update.message.reply_text(f"✅ UID {uid} đang LIVE!")
    else:
        await update.message.reply_text(f"❌ UID {uid} không live.")

bot = Application.builder().token(TOKEN).build()
bot.add_handler(CommandHandler("start", start))
bot.add_handler(CommandHandler("check", check))

@app.route("/")
def home():
    return "✅ FB Live Bot is running!"

def run():
    Thread(target=lambda: bot.run_polling()).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    run()
