import logging
import os
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import Application, ContextTypes, CommandHandler, MessageHandler, filters
from flask import Flask, request
import asyncio

# --- Basic Setup ---
logging.basicConfig(format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO)
logger = logging.getLogger(__name__)

# --- Configuration ---
TOKEN = os.environ.get("BOT_TOKEN")
APP_URL = os.environ.get("RENDER_APP_URL")

# --- Tesseract Path Setup ---
tesseract_cmd = os.environ.get('TESSERACT_CMD')
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# --- PTB and Flask App Initialization ---
ptb_app = Application.builder().token(TOKEN).build()
flask_app = Flask(__name__)

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text("שלום! שלח לי תמונה (או קובץ תמונה) ואפיק ממנה את הטקסט.")

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("מעבד את התמונה...", quote=True)
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"{photo_file.file_id}.jpg"
        await photo_file.download_to_drive(file_path)
        extracted_text = pytesseract.image_to_string(Image.open(file_path), lang='heb+eng')
        os.remove(file_path)
        await update.message.reply_text(extracted_text or "לא נמצא טקסט.", quote=True)
    except Exception as e:
        logger.error(f"Error handling image: {e}")
        await update.message.reply_text("אירעה שגיאה בעיבוד התמונה.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# --- Flask Webhook Endpoint ---
@flask_app.route(f"/{TOKEN}", methods=["POST"])
def respond():
    update = Update.de_json(request.get_json(force=True), ptb_app.bot)
    asyncio.run(ptb_app.process_update(update))
    return "ok"

# --- Main Setup Coroutine ---
async def main():
    ptb_app.add_error_handler(error_handler)
    ptb_app.add_handler(CommandHandler("start", start))
    ptb_app.add_handler(MessageHandler(filters.PHOTO, handle_image))
    ptb_app.add_handler(MessageHandler(filters.Document.IMAGE, handle_image))
    
    await ptb_app.initialize()
    webhook_url = f"{APP_URL}/{TOKEN}"
    await ptb_app.bot.set_webhook(url=webhook_url, allowed_updates=Update.ALL_TYPES)
    logger.info(f"Webhook set to {webhook_url}")

# Run the setup once when the app starts
asyncio.run(main())
