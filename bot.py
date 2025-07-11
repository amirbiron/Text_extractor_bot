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

# --- הגדרות ראשוניות ---
try:
    Config.validate()
except AttributeError:
    pass

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
)
logger = logging.getLogger(__name__)

if os.getenv('TESSERACT_PATH'):
    pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

# --- אתחול Flask ---
app = Flask(__name__)

# --- לוגיקת הבוט ---
async def start(update: Update, context):
    await update.message.reply_text(os.getenv('WELCOME_MESSAGE', 'Welcome! Send me an image to extract text.'))

async def help_command(update: Update, context):
    await update.message.reply_text(os.getenv('HELP_MESSAGE', 'Send a photo and I will extract the text. That\'s it!'))

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
        try:
            await update.message.reply_text("❌ אירעה שגיאה בעיבוד התמונה.")
        except Exception as inner_e:
            logger.error(f"Failed to send error message: {inner_e}")

async def handle_text(update: Update, context):
    await update.message.reply_text("📸 אנא שלחו תמונה כדי לחלץ ממנה טקסט.")

# --- אתחול הבוט ---
application = Application.builder().token(Config.BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# --- נתיבי Flask ---
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

# --- פונקציית הרצה מותאמת ---
async def run_bot():
    webhook_url = os.getenv('WEBHOOK_URL')
    if webhook_url:
        await application.initialize()
        await application.bot.set_webhook(
            url=f"{webhook_url}/webhook",
            allowed_updates=Update.ALL_TYPES
        )
        logger.info(f"✅ Webhook set to: {webhook_url}/webhook")
        port = int(os.getenv('PORT', 8080))
        app.run(host='0.0.0.0', port=port)
    else:
        logger.info("🟡 No WEBHOOK_URL found, running in polling mode...")
        await application.run_polling()

# --- נקודת כניסה ---
if __name__ == '__main__':
    asyncio.run(run_bot())
