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
    # Handle case where Config class might not have validate method
    pass

logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, os.getenv('LOG_LEVEL', 'INFO').upper())
)
logger = logging.getLogger(__name__)
if os.getenv('TESSERACT_PATH'):
    pytesseract.pytesseract.tesseract_cmd = os.getenv('TESSERACT_PATH')

# --- אתחול אפליקציית Flask ---
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
        
        # הורדה וחילוץ טקסט
        url = f"https://api.telegram.org/file/bot{Config.BOT_TOKEN}/{file.file_path}"
        response = requests.get(url)
        response.raise_for_status()
        image = Image.open(io.BytesIO(response.content)).convert('RGB')
        text = pytesseract.image_to_string(image, lang='heb+eng')
        
        await loading_msg.delete()
        if text.strip():
            response_text = f"📝 **הטקסט שנמצא בתמונה:**\n\n{text.strip()}"
            await update.message.reply_text(response_text, parse_mode='Markdown')
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

# --- הגדרת הבוט ---
application = Application.builder().token(Config.BOT_TOKEN).build()
application.add_handler(CommandHandler("start", start))
application.add_handler(CommandHandler("help", help_command))
application.add_handler(MessageHandler(filters.PHOTO, handle_photo))
application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text))

# --- נתיבי שרת ה-Flask ---
@app.route('/webhook', methods=['POST'])
async def webhook():
    """Endpoint to receive updates from Telegram."""
    update_data = request.get_json()
    # Process update in the background
    await application.update_queue.put(Update.de_json(update_data, application.bot))
    return jsonify({"status": "OK"}), 200

@app.route('/health', methods=['GET'])
def health_check():
    """Health check endpoint for Render."""
    return jsonify({"status": "OK"}), 200

@app.route('/', methods=['GET'])
def index():
    """Homepage to confirm the bot is running."""
    return jsonify({"message": "Bot is running and listening for webhooks"}), 200

# --- פונקציית הרצה ראשית ---
async def main():
    """Initialize the bot and set the webhook."""
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        logger.error("FATAL: WEBHOOK_URL environment variable is not set!")
        return

    await application.initialize()
    await application.bot.set_webhook(
        url=f"{webhook_url}/webhook",
        allowed_updates=Update.ALL_TYPES
    )
    logger.info(f"Webhook has been set to {webhook_url}/webhook")

if __name__ == '__main__':
    # Initialize the bot and webhook
    loop = asyncio.get_event_loop()
    loop.run_until_complete(main())
    
    # Start the Flask server
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port)
