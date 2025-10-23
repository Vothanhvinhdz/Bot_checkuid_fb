from flask import Flask, request
import requests
import os

app = Flask(__name__)

# ----------------------------
# Cấu hình
# ----------------------------
BOT_TOKEN = os.environ.get("7618142601:AAH4_zzpHyy7wjioC9QbBCtXcuNO-roKl8s")  # Token bot Telegram từ BotFather
WEBHOOK_URL = os.environ.get("https://abcd1234.ngrok.io/webhook")  # URL server public HTTPS
TELEGRAM_API_URL = f"https://api.telegram.org/bot{BOT_TOKEN}"
# ----------------------------

# 1️⃣ Hàm gửi tin nhắn reply
def send_message(chat_id, text):
    requests.post(f"{TELEGRAM_API_URL}/sendMessage", data={
        "chat_id": chat_id,
        "text": text
    })

# 2️⃣ Route nhận webhook
@app.route("/webhook", methods=["POST"])
def webhook():
    data = request.json
    print("Received update:", data)

    if "message" in data:
        chat_id = data["message"]["chat"]["id"]
        text = data["message"].get("text", "")
        reply_text = f"Bạn vừa gửi: {text}"

        send_message(chat_id, reply_text)

    return "OK", 200

# 3️⃣ Hàm set webhook (chạy 1 lần để register Telegram)
def set_webhook():
    response = requests.post(f"{TELEGRAM_API_URL}/setWebhook", data={
        "url": WEBHOOK_URL
    })
    print("Set webhook:", response.json())

# 4️⃣ Chạy server Flask
if __name__ == "__main__":
    # Chỉ set webhook khi chạy lần đầu
    set_webhook()
    # Chạy server
    port = int(os.environ.get("PORT", 5000))  # Replit/Render sẽ set PORT
    app.run(host="0.0.0.0", port=port)
