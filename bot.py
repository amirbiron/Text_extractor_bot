import logging
import os
import io
import asyncio
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from PIL import Image
import pytesseract
import requests
from config import Config

# --- הגדרות בסיס ---
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
)
logger = logging.getLogger(__name__)

if os.getenv('TESSERACT_PATH'):
    pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

# --- אתחול Flask ---
app = Flask(__name__)

# --- אתחול הבוט ---
application = Application.builder().token(Config.BOT_TOKEN).build()

# --- פקודות הבוט ---
async def start(update: Update, context):
    await update.message.reply_text(os.getenv('WELCOME_MESSAGE', '👋 ברוכים הבאים! שלחו לי תמונה ואזהה את הטקסט שבה.'))

async def help_command(update: Update, context):
    await update.message.reply_text(os.getenv('HELP_MESSAGE', '📸 שלחו תמונה עם טקסט ואחזיר לכם את מה שמופיע בה.'))

async def handle_photo(update: Update, context):
    try:
        loading_msg = await update.message.reply_text("🔄 מעבד את התמונה...")
        photo = update.message.photo[-1]
        file = await context.bot.get_file(photo.file_id)
        url = f"https://api.telegram.org/file/bot{Config.BOT_TOKEN}/{file.file_path}"
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        text = pytesseract.image_to_string(image, lang='heb+eng')

        await loading_msg.delete()
        if text.strip():
            await update.message.reply_text(f"📝 **הטקסט שנמצא בתמונה:**\n\n{text.strip()}", parse_mode='Markdown')
        else:
            await update.message.reply_text("❌ לא נמצא טקסט בתמונה.")
    except Exception as e:
        logger.error(f"שגיאה בעיבוד תמונה: {e}")
        await update.message.reply_text("❌ אירעה שגיאה בעיבוד התמונה.")

async def handle_text(update: Update, context):
    await update.message.reply_text("📸 שלחו תמונה כדי שאזהה את הטקסט שבה.")

# --- רישום handlers ---
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# --- מסלולים של Flask ---
@app.route('/webhook', methods=['POST'])
async def webhook():
    update_data = request.get_json()
    await application.update_queue.put(Update.de_json(update_data, application.bot))
    return jsonify({"status": "OK"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    return jsonify({"status": "OK"}), 200

@app.route('/', methods=['GET'])
def index():
    return jsonify({"message": "Bot is running and listening for webhooks"}), 200

# --- רישום ה־Webhook כששרת עולה ---
webhook_url = os.getenv('WEBHOOK_URL')
if webhook_url:
    asyncio.get_event_loop().create_task(application.initialize())
    asyncio.get_event_loop().create_task(application.bot.set_webhook(
        url=f"{webhook_url}/webhook",
        allowed_updates=Update.ALL_TYPES
    ))
    logger.info(f"✅ Webhook set to: {webhook_url}/webhook")
