import requests
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, ContextTypes
import os

# Lấy token từ biến môi trường (Render sẽ dùng)
BOT_TOKEN = os.getenv"8297940469:AAHo6FwJebpHbkll5idwZ92r_ANeMoJv1yM"

# --- Hàm kiểm tra UID ---
def check_facebook_uid(uid):
    url = f"https://graph.facebook.com/{uid}"
    try:
        r = requests.get(url, timeout=5)
        if r.status_code == 200 and "id" in r.text:
            return "LIVE"
        else:
            return "DIE"
    except:
        return "DIE"

# --- Lệnh /check ---
async def check(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if len(context.args) == 0:
        await update.message.reply_text("⚠️ Vui lòng nhập UID!\nVí dụ: /check 1000123456789")
        return

    uid = context.args[0]
    await update.message.reply_text(f"🔍 Đang kiểm tra UID {uid}...")

    status = check_facebook_uid(uid)

    if status == "LIVE":
        await update.message.reply_text(f"✅ UID {uid} đang **LIVE** (tồn tại).")
    else:
        await update.message.reply_text(f"❌ UID {uid} đã **DIE** hoặc không tồn tại.")

# --- Khởi tạo bot ---
app = ApplicationBuilder().token(BOT_TOKEN).build()
app.add_handler(CommandHandler("check", check))

if __name__ == "__main__":
    print("🤖 Bot đang chạy...")
    app.run_polling()
