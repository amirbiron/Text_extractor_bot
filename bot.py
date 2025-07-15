import logging
import os
import pytesseract
from PIL import Image
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import http.server
import socketserver
import threading

# --- Basic Setup ---
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s", level=logging.INFO
)
logger = logging.getLogger(__name__)

# --- Configuration ---
TOKEN = os.environ.get("BOT_TOKEN")
TESSERACT_CMD_PATH = os.environ.get('TESSERACT_CMD')
PORT = 8080

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
            
    except Exception as e:
        logger.error(f"Exception while handling image: {e}", exc_info=True)
        await update.message.reply_text("אירעה שגיאה בעיבוד התמונה. ייתכן שתוכנת זיהוי הטקסט לא הותקנה כראוי על השרת.")

async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# --- Main Application Runner ---
def main() -> None:
    # Validate environment variables before starting
    if not TOKEN:
        logger.fatal("FATAL: BOT_TOKEN environment variable is missing! Application will exit.")
        exit(1)
    if not TESSERACT_CMD_PATH:
        logger.fatal("FATAL: TESSERACT_CMD environment variable is missing! Application will exit.")
        exit(1)
    
    # Set Tesseract path for the pytesseract library
    pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH
    
    # Start the keep-alive server in a separate thread
    keep_alive_thread = threading.Thread(target=run_keep_alive_server)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    # Create and run the Telegram bot
    application = Application.builder().token(TOKEN).build()
    
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_image))
    
    logger.info("Bot starting with Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
