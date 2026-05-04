import os
from pyrogram import Client, filters
import requests

API_ID = int(os.getenv("API_ID"))
API_HASH = os.getenv("API_HASH") 
BOT_TOKEN = os.getenv("BOT_TOKEN")
GITHUB_TOKEN = os.getenv("GITHUB_TOKEN") # لازم نضيفه
REPO = "abuhoney/blender-bot" # غيره لو الريبو مختلف

app = Client("action_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

@app.on_message(filters.command("start"))
async def start(c, m):
    await m.reply("هلا عزي\nأرسل ملف .py عشان أرندره لك على GitHub بجودة 4K")

@app.on_message(filters.document & filters.private)
async def handle_doc(c, m):
    if not m.document.file_name.endswith('.py'):
        return await m.reply("❌ أرسل ملف بايثون فقط")
    
    msg = await m.reply("⚙️ جاري رفع الملف وتشغيل الرندر على GitHub...")
    
    # 1. نشغل الـ GitHub Action
    headers = {"Authorization": f"token {GITHUB_TOKEN}", "Accept": "application/vnd.github.v3+json"}
    data = {
        "ref": "main",
        "inputs": {
            "script_name": m.document.file_id,
            "chat_id": str(m.chat.id)
        }
    }
    r = requests.post(f"https://api.github.com/repos/{REPO}/actions/workflows/render.yml/dispatches", headers=headers, json=data)
    
    if r.status_code == 204:
        await msg.edit("✅ تم تشغيل الرندر بنجاح!\nالمدة المتوقعة 3-15 دقيقة حسب طول الفيديو.\nبرسل لك الفيديو هنا لما يخلص.")
    else:
        await msg.edit(f"❌ فشل تشغيل الرندر: {r.text}")

app.run()
