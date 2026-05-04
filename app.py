import asyncio
import sys
import os
import requests
from pyrogram import Client, filters
from pyrogram.types import Message
from threading import Thread
from flask import Flask

# ========= سيرفر وهمي عشان Render =========
web_app = Flask(__name__)

@web_app.route('/')
def home():
    return "Blender Bot is Running ✅"

def run_web():
    port = int(os.environ.get('PORT', 10000))
    web_app.run(host='0.0.0.0', port=port)

Thread(target=run_web, daemon=True).start()
# =========================================

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

# ========= المتغيرات من Render =========
API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")
GITHUB_TOKEN = os.environ.get("GITHUB_TOKEN")
GITHUB_REPO = "abuhoney/blender-bot"  # غيره لو اسم الريبو حقك مختلف
# ======================================

app = Client("blender_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    await message.reply_text("""هلا عزيزي 🚀

أرسل لي ملف .py حق Blender وأنا بشغله على GitHub Actions 
برام 7GB وبجودة 1080p أو 4K

الوقت المتوقع: 3-10 دقايق حسب الجودة

أرسل الملف الحين 👇""")

@app.on_message(filters.document & filters.private)
async def handle_file(client: Client, message: Message):
    if not message.document.file_name.endswith(".py"):
        await message.reply_text("❌ أرسل ملف بصيغة .py فقط")
        return

    status_msg = await message.reply_text("⏳ جاري استلام الملف...")
    
    try:
        # 1. نزل الملف من تليجرام
        script_content = await message.download(in_memory=True)
        script_text = script_content.getvalue().decode('utf-8')
        
        await status_msg.edit_text("⚙️ جاري تشغيل الرندر على GitHub Actions...\nبياخذ 3-10 دقايق حسب الجودة")

        # 2. شغل الـ workflow في GitHub
        headers = {
            "Authorization": f"token {GITHUB_TOKEN}",
            "Accept": "application/vnd.github.v3+json"
        }
        data = {
            "ref": "main",
            "inputs": {
                "script_content": script_text,
                "chat_id": str(message.chat.id)
            }
        }
        url = f"https://api.github.com/repos/{GITHUB_REPO}/actions/workflows/render.yml/dispatches"
        
        response = requests.post(url, headers=headers, json=data)
        
        if response.status_code == 204:
            await status_msg.edit_text("✅ تم تشغيل الرندر بنجاح!\n\nتابع التقدم:\nhttps://github.com/" + GITHUB_REPO + "/actions\n\nالفيديو بيوصل هنا تلقائي لما يخلص 🎬")
        else:
            await status_msg.edit_text(f"❌ فشل تشغيل الرندر:\nالكود: {response.status_code}\n{response.text[:500]}")
            
    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ: {str(e)[:500]}")

if __name__ == "__main__":
    print("Bot Started...")
    app.run()
