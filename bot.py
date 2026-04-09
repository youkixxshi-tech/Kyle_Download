import os
import telebot
import yt_dlp
from flask import Flask
from threading import Thread

# --- Bot Token ထည့်ရန်နေရာ ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"
bot = telebot.TeleBot(TOKEN)
app = Flask(__name__)

# Render Health Check (Render Fail မဖြစ်စေရန် အရေးကြီးဆုံးအပိုင်း)
@app.route('/')
def home():
    return "Bot is Active!", 200

# TikTok Downloader Function
def download_tiktok(url):
    ydl_opts = {
        'format': 'best',
        'outtmpl': 'video.mp4',
        'quiet': True,
        'no_warnings': True,
        # TikTok က ပိတ်တာကို ကာကွယ်ဖို့
        'http_headers': {
            'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/91.0.4472.124 Safari/537.36'
        }
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        ydl.download([url])
        return 'video.mp4'

@bot.message_handler(commands=['start'])
def welcome(message):
    bot.reply_to(message, "TikTok link ပို့ပေးပါ၊ ဒေါင်းပေးပါ့မယ်။")

@bot.message_handler(func=lambda m: "tiktok.com" in m.text or "douyin.com" in m.text)
def handle_tiktok(message):
    wait = bot.reply_to(message, "⏳ ခဏစောင့်ပါ...")
    try:
        file = download_tiktok(message.text)
        with open(file, 'rb') as v:
            bot.send_video(message.chat.id, v)
        if os.path.exists(file):
            os.remove(file)
        bot.delete_message(message.chat.id, wait.message_id)
    except Exception as e:
        bot.edit_message_text(f"❌ Error တက်သွားပါတယ်- ပြန်စမ်းကြည့်ပါ။", message.chat.id, wait.message_id)

def run_bot():
    bot.infinity_polling(timeout=10, long_polling_timeout=5)

if __name__ == "__main__":
    # 1. Bot ကို Background မှာ Run မယ်
    Thread(target=run_bot).start()
    # 2. Flask Server ကို Render ပေးတဲ့ Port မှာ Run မယ်
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)
