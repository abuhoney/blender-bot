import asyncio
import sys
import os
import uuid
import shutil
import psutil
from pyrogram import Client, filters
from pyrogram.types import Message

if sys.platform == "win32":
    asyncio.set_event_loop_policy(asyncio.WindowsSelectorEventLoopPolicy())
try:
    asyncio.get_running_loop()
except RuntimeError:
    asyncio.set_event_loop(asyncio.new_event_loop())

API_ID = int(os.environ.get("API_ID"))
API_HASH = os.environ.get("API_HASH")
BOT_TOKEN = os.environ.get("BOT_TOKEN")

app = Client("render_bot", api_id=API_ID, api_hash=API_HASH, bot_token=BOT_TOKEN)

TEMP_DIR = "temp_jobs"
MAX_EXECUTION_TIME = 900 # 15 دقيقة عشان الرندر

if not os.path.exists(TEMP_DIR):
    os.makedirs(TEMP_DIR)

@app.on_message(filters.command("start"))
async def start_command(client: Client, message: Message):
    welcome_text = """========
هلا عزيزي
أرسل لي ملف الكود الخاص بإنشاء أي فيديو سأقوم بمعالجة ذلك وإرجاع مقطع فيديو جاهز يتناسب مع جميع الشاشات معا الحفاظ على الدقة وموازنه الصوت والنص والمواقف

أرسله الآن 👇
========"""
    await message.reply_text(welcome_text)

@app.on_message(filters.document & filters.private)
async def handle_file(client: Client, message: Message):
    if not message.document.file_name.endswith(".py"):
        await message.reply_text("❌ أرسل ملف بصيغة.py فقط")
        return

    job_id = str(uuid.uuid4())
    job_dir = os.path.join(TEMP_DIR, job_id)
    os.makedirs(job_dir)
    status_msg = await message.reply_text("⏳ جاري استلام الملف...")

    try:
        file_path = os.path.join(job_dir, "script.py")
        await message.download(file_name=file_path)
        await status_msg.edit_text("⚙️ جاري تنفيذ الكود... الرندر ياخذ 8-12 دقيقة")
        output_path = os.path.join(job_dir, "output.mp4")

        # هذا السطر يشغل Blender
        process = await asyncio.create_subprocess_exec(
            "blender", "--background", "--python", file_path, "--", output_path,
            stdout=asyncio.subprocess.PIPE, stderr=asyncio.subprocess.PIPE
        )

        try:
            stdout, stderr = await asyncio.wait_for(process.communicate(), timeout=MAX_EXECUTION_TIME)
        except asyncio.TimeoutError:
            await status_msg.edit_text("❌ انتهى الوقت المحدد 15 دقيقة")
            shutil.rmtree(job_dir)
            return

        if process.returncode != 0:
            error_text = stderr.decode()[:1000]
            await status_msg.edit_text(f"❌ فشل تنفيذ الكود:\n\n<code>{error_text}</code>")
            shutil.rmtree(job_dir)
            return

        if not os.path.exists(output_path):
            await status_msg.edit_text("❌ لم يتم العثور على output.mp4")
            shutil.rmtree(job_dir)
            return

        await status_msg.edit_text("📤 جاري رفع الفيديو...")
        await client.send_video(
            chat_id=message.chat.id,
            video=output_path,
            caption="✅ تم إنشاء الفيديو بنجاح 1080p",
            supports_streaming=True
        )
        await status_msg.delete()
    except Exception as e:
        await status_msg.edit_text(f"❌ خطأ: {str(e)[:500]}")
    finally:
        if os.path.exists(job_dir):
            shutil.rmtree(job_dir)

app.run()