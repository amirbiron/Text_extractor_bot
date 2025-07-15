import logging
import os
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import http.server
import socketserver
import threading

# --- Diagnostic Block at the very top ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- Starting Diagnostic Check ---")
bot_token_found = os.environ.get("BOT_TOKEN")
tesseract_cmd_found = os.environ.get("TESSERACT_CMD")

logger.info(f"Found BOT_TOKEN: {'Yes, value is present.' if bot_token_found else 'No, value is missing!'}")
logger.info(f"Found TESSERACT_CMD: {'Yes, value is present.' if tesseract_cmd_found else 'No, value is missing!'}")
logger.info(f"Value for TESSERACT_CMD from environment: {tesseract_cmd_found}")

if not bot_token_found or not tesseract_cmd_found:
    logger.error("FATAL: A required environment variable is missing. The application will now exit.")
    exit()
else:
    logger.info("--- Diagnostic Check Passed. Starting bot... ---")
# --- End of Diagnostic block ---

# --- Configuration ---
TOKEN = bot_token_found
PORT = 8080
pytesseract.pytesseract.tesseract_cmd = tesseract_cmd_found


# --- Keep-Alive Web Server ---
def run_keep_alive_server():
    handler = http.server.SimpleHTTPRequestHandler
    with socketserver.TCPServer(("", PORT), handler) as httpd:
        logger.info(f"Keep-alive server started on port {PORT}")
        httpd.serve_forever()

# --- Bot Handlers ---
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    await update.message.reply_text(
        "שלום! שלח לי תמונה (או קובץ תמונה) ואפיק ממנה את הטקסט בעברית או באנגלית."
    )

async def handle_image(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    try:
        await update.message.reply_text("מעבד את התמונה...", quote=True)
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"{photo_file.file_id}.jpg"
        await photo_file.download_to_drive(file_path)
        
        extracted_text = pytesseract.image_to_string(Image.open(file_path), lang='heb+eng')
        
        os.remove(file_path)
        
        if extracted_text.strip():
            await update.message.reply_text(extracted_text, quote=True)
        else:
            await update.message.reply_text("לא הצלחתי למצוא טקסט בתמונה.", quote=True)
            
    except Exception:
        logger.error("Exception while handling image:", exc_info=True)
        await update.message.reply_text("אירעה שגיאה בעיבוד התמונה.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# --- Main Application Runner ---
def main() -> None:
    keep_alive_thread = threading.Thread(target=run_keep_alive_server)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    application = Application.builder().token(TOKEN).build()
    
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_image))
    
    logger.info("Bot starting with Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
