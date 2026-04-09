import os
import requests
import re
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (Render အတွက်) ---
app = Flask('')

@app.route('/')
def home():
    return "TikTok Bot is Alive! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app.run(host='0.0.0.0', port=port)

# --- 2. Configuration ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"
TIKTOK_API = "https://www.tikwm.com/api/"

# --- 3. TikTok Logic ---
async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    
    # TikTok Link ပါသလား ရှာမယ်
    if "tiktok.com" in text:
        links = re.findall(r'(https?://[^\s]+)', text)
        if not links:
            return
            
        tiktok_url = links[0]
        status_msg = await update.message.reply_text("ဗီဒီယို ရှာနေပါတယ်... ⏳")

        try:
            # API ခေါ်ယူခြင်း
            response = requests.get(TIKTOK_API, params={'url': tiktok_url}).json()

            if response.get('code') == 0:
                data = response['data']
                video_url = data['play']
                
                # ဗီဒီယို ပို့ခြင်း
                await update.message.reply_video(
                    video=video_url,
                    caption="✅ Downloaded successfully!"
                )
                await status_msg.delete()
            else:
                await status_msg.edit_text("❌ ဗီဒီယို ရှာမတွေ့ပါ။ Link ပြန်စစ်ပေးပါ။")
        except Exception as e:
            print(f"Error: {e}")
            await status_msg.edit_text("⚠️ Error တက်သွားပါတယ်။ ခဏနေမှ ပြန်စမ်းပါ။")

# --- 4. Main Function ---
def main():
    # Web Server ကို Thread နဲ့ အရင်ဖွင့်မယ်
    Thread(target=run_web).start()
    
    # Bot ကို စတင်မယ်
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    
    print("Bot is polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
