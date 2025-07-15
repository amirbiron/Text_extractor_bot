import os
import logging
import time

# --- NEW: Delay for environment stabilization ---
print("--- Script started, waiting 5 seconds for environment to stabilize... ---")
time.sleep(5)

# --- NEW: Verbose Diagnostic Block ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- Starting Verbose Diagnostic Check ---")
logger.info("--- All available environment variables: ---")
for key, value in os.environ.items():
    # Mask sensitive values for security
    if "TOKEN" in key.upper() or "KEY" in key.upper() or "URI" in key.upper():
        value = f"{value[:4]}...{value[-4:]}" if len(value) > 8 else "***"
    logger.info(f"'{key}': '{value}'")
logger.info("-----------------------------------------")

bot_token = os.environ.get("BOT_TOKEN")
tesseract_cmd = os.environ.get("TESSERACT_CMD")

if not bot_token or not tesseract_cmd:
    logger.error("FATAL: A required environment variable (BOT_TOKEN or TESSERACT_CMD) is missing or empty.")
    logger.error("The bot cannot start. This container will now idle for 10 minutes for debugging.")
    time.sleep(600) # Keep the container alive so we can read the logs
    exit(1) # Exit with an error code after idling
else:
    logger.info("--- Diagnostic Check Passed. Proceeding with bot startup... ---")

# --- If diagnostics passed, the original bot code runs ---
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import http.server
import socketserver
import threading

# --- Configuration ---
TOKEN = bot_token
PORT = 8080
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd

# --- Keep-Alive Web Server ---
def run_keep_alive_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        logger.info(f"Keep-alive server started on port {PORT}")
        httpd.serve_forever()

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "שלום! שלח לי תמונה ואפיק ממנה את הטקסט."
    )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("מעבד את התמונה...", quote=True)
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"{photo_file.file_id}.jpg"
        await photo_file.download_to_drive(file_path)
        extracted_text = pytesseract.image_to_string(Image.open(file_path), lang='heb+eng')
        os.remove(file_path)
        await update.message.reply_text(extracted_text or "לא נמצא טקסט.", quote=True)
    except Exception:
        logger.error("Exception while handling image:", exc_info=True)
        await update.message.reply_text("אירעה שגיאה בעיבוד התמונה.")

# --- Main Application Runner ---
def main() -> None:
    keep_alive_thread = threading.Thread(target=run_keep_alive_server)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    application = Application.builder().token(TOKEN).build()
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_image))
    
    logger.info("Bot starting with Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
