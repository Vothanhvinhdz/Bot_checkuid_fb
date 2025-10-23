import os
import requests
import sqlite3
from flask import Flask, request, jsonify
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

TOKEN = os.getenv("7618142601:AAH4_zzpHyy7wjioC9QbBCtXcuNO-roKl8s")
FB_TOKEN = os.getenv("EAAGNO4a7r2wBPyLgahrnYRBnA4qQKZAlY5aofyumyBqHRhPZCwOzCSevSOiaaGpWCxZABbm9OMeYMghSZA4q3KPfnmcw396tQPGI9cTZAqF9feQn33HJtjj4QqGa3ZCiD7EXZCGZCgxbwPpWFvLCywzZCY74Gd9Aa8xOoWkphBvZAUFrUsap7GrcnOoOjfsWmYSHCJtwZDZD")
GRAPH_VERSION = os.getenv("EAASZCdhyolicBPzGhj8eRpwOfrWAZC1zIWDXY7pZC6yUutfN8Bob2yNebwxoIr9sNNmqzJBBNuYPer0MUPTOmfWZAm2ZCLUVExZBxHZCYZBUN3DZAEy6BZAwFSugy4sP4rmglN6xRpaKpjJ3XyrR0FX5g8RMZAqavUBj1LnqUfobfev2aHdpD2Kj6XjhaKSD6nxWrbr", "v19.0")

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("👋 Xin chào! Gửi /check <uid> để kiểm tra live.")

async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not context.args:
        await update.message.reply_text("❗ Vui lòng nhập UID sau lệnh /check")
        return
    uid = context.args[0]
    url = f"https://graph.facebook.com/{GRAPH_VERSION}/{uid}/live_videos"
    r = requests.get(url, params={"access_token": FB_TOKEN})
    if "data" in r.json() and len(r.json()["data"]) > 0:
        await update.message.reply_text(f"✅ UID {uid} đang LIVE!")
    else:
        await update.message.reply_text(f"❌ UID {uid} không live.")

bot_app = Application.builder().token(TOKEN).build()
bot_app.add_handler(CommandHandler("start", start))
bot_app.add_handler(CommandHandler("check", check))

@app.route("/fb/webhook", methods=["GET", "POST"])
def fb_webhook():
    VERIFY_TOKEN = os.getenv("WEBHOOK_VERIFY_TOKEN")
    if request.method == "GET":
        if request.args.get("hub.verify_token") == VERIFY_TOKEN:
            return request.args.get("hub.challenge")
        return "Verification failed", 403

    if request.method == "POST":
        data = request.get_json()
        print("📩 Webhook data:", data)
        if data and "entry" in data:
            for entry in data["entry"]:
                if "changes" in entry:
                    for change in entry["changes"]:
                        if change["field"] == "live_videos":
                            live_id = change["value"].get("id", "")
                            uid = change["value"].get("from", {}).get("id", "")
                            msg = f"📺 UID {uid} vừa bắt đầu livestream!\nLive ID: {live_id}"
                            notify_all(msg)
        return "ok"

def notify_all(msg):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("SELECT chat_id FROM subs")
    subs = cur.fetchall()
    conn.close()
    for s in subs:
        chat_id = s[0]
        requests.post(
            f"https://api.telegram.org/bot{TOKEN}/sendMessage",
            json={"chat_id": chat_id, "text": msg},
        )

@app.route("/")
def home():
    return "✅ FB Live Bot is running!"

def run():
    from threading import Thread
    Thread(target=lambda: bot_app.run_polling()).start()
    app.run(host="0.0.0.0", port=int(os.getenv("PORT", 5000)))

if __name__ == "__main__":
    run()