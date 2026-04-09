import os
import re
import aiohttp
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (Render 24/7 အတွက်) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "TikTok Bot is Online! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. Configuration ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g"
TIKTOK_API = "https://www.tikwm.com/api/"

# --- 3. TikTok Logic (Asynchronous Version) ---
async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    text = update.message.text
    
    if "tiktok.com" in text:
        links = re.findall(r'(https?://[^\s]+)', text)
        if not links:
            return
            
        tiktok_url = links[0]
        status_msg = await update.message.reply_text("ဗီဒီယို ရှာနေပါတယ်... ⏳")

        try:
            # aiohttp ကိုသုံးပြီး Video ဆွဲမယ် (ပိုမြန်ပြီး Error ကင်းတယ်)
            async with aiohttp.ClientSession() as session:
                async with session.get(TIKTOK_API, params={'url': tiktok_url}) as response:
                    data_json = await response.json()

                    if data_json.get('code') == 0:
                        video_data = data_json['data']
                        video_url = video_data['play']
                        
                        await update.message.reply_video(
                            video=video_url,
                            caption="✅ Watermark မပါဘဲ ဒေါင်းလုဒ်ဆွဲပြီးပါပြီ။"
                        )
                        await status_msg.delete()
                    else:
                        await status_msg.edit_text("❌ ဗီဒီယို ရှာမတွေ့ပါ။ Link ပြန်စစ်ပေးပါ။")
        except Exception as e:
            print(f"Error: {e}")
            await status_msg.edit_text("⚠️ API Error တက်သွားပါတယ်။ ခဏနေမှ ပြန်စမ်းပါ။")

# --- 4. Main Function ---
if __name__ == "__main__":
    # Web Server ကို Thread နဲ့ Background မှာ ပတ်မယ်
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Bot စတင်ခြင်း
    print("Bot is Starting...")
    application = Application.builder().token(TOKEN).build()
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    
    application.run_polling()
