import os
import requests
import re
from flask import Flask
from threading import Thread
from telegram import Update
from telegram.ext import Application, MessageHandler, filters, ContextTypes

# --- 1. Flask Web Server (For Render 24/7) ---
app_web = Flask('')

@app_web.route('/')
def home():
    return "TikTok Downloader Bot is Online! 🚀"

def run_web():
    port = int(os.environ.get("PORT", 10000))
    app_web.run(host='0.0.0.0', port=port)

# --- 2. Configuration ---
TOKEN = "8528856013:AAHGQf6IeVVBhWOOmhIWTedX4UOkHnDZB5g" # မင်းရဲ့ Bot Token
TIKTOK_API = "https://www.tikwm.com/api/"

# --- 3. TikTok Logic ---
async def handle_tiktok(update: Update, context: ContextTypes.DEFAULT_TYPE):
    if not update.message or not update.message.text:
        return

    message_text = update.message.text
    
    # TikTok Link ဟုတ်မဟုတ် စစ်ဆေးခြင်း (vm.tiktok.com သို့မဟုတ် vt.tiktok.com စသည်ဖြင့်)
    if "tiktok.com" in message_text:
        # Link ကို သီးသန့်ခွဲထုတ်မယ်
        links = re.findall(r'(https?://[^\s]+)', message_text)
        if not links:
            return
            
        tiktok_url = links[0]
        status_msg = await update.message.reply_text("ဗီဒီယိုကို ရှာဖွေနေပါတယ်... ခဏစောင့်ပေးပါဦး ⏳")

        try:
            # TikWM API ဆီကနေ data လှမ်းတောင်းမယ်
            response = requests.get(TIKTOK_API, params={'url': tiktok_url}).json()

            if response.get('code') == 0:
                data = response['data']
                video_url = data['play'] # No Watermark Video
                title = data.get('title', 'No Title')
                nickname = data.get('author', {}).get('nickname', 'Unknown')

                # ဗီဒီယိုကို ပို့ပေးမယ်
                await update.message.reply_video(
                    video=video_url,
                    caption=f"👤 **Author:** {nickname}\n📝 **Title:** {title}\n\nDownloaded by Your Bot ✅",
                    parse_mode='Markdown'
                )
                await status_msg.delete() # 'ရှာဖွေနေပါတယ်' ဆိုတဲ့စာကို ပြန်ဖျက်မယ်
            else:
                await status_msg.edit_text("❌ ဗီဒီယို ရှာမတွေ့ပါဘူး။ Link မှန်ရဲ့လား ပြန်စစ်ပေးပါ။")

        except Exception as e:
            print(f"Error: {e}")
            await status_msg.edit_text("⚠️ အမှားတစ်ခုခု တက်သွားပါတယ်။ ခဏနေမှ ပြန်စမ်းကြည့်ပါ။")

# --- 4. Main Execution ---
if __name__ == "__main__":
    # Web server ကို Thread နဲ့ ပတ်မယ်
    t = Thread(target=run_web)
    t.daemon = True
    t.start()
    
    # Telegram Bot ကို စတင်မယ်
    print("Bot starting...")
    app = Application.builder().token(TOKEN).build()
    
    # Message Handler (စာသားထဲမှာ tiktok ပါတာနဲ့ အလုပ်လုပ်မယ်)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_tiktok))
    
    print("TikTok Downloader Bot is Ready!")
    app.run_polling()
