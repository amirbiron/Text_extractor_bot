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

TOKEN = os.environ.get("BOT_TOKEN")
PORT = 8080 # Port for the keep-alive server

# --- NEW: Explicitly set the Tesseract command path ---
# This line reads the path from an environment variable we will set in Render.
# This is the fix for the "tesseract is not installed" error.
tesseract_cmd = os.environ.get('TESSERACT_CMD')
if tesseract_cmd:
    pytesseract.pytesseract.tesseract_cmd = tesseract_cmd
else:
    logger.warning("TESSERACT_CMD environment variable not set. Assuming Tesseract is in PATH.")


# --- Keep-Alive Web Server ---
def run_keep_alive_server():
    """Runs a simple HTTP server in a background thread to keep the service alive."""
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
    """Handles photo messages and extracts text from them."""
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
        logger.error(f"Error handling image: {e}")
        await update.message.reply_text("אירעה שגיאה בעיבוד התמונה.")

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    """Handles image files sent as documents."""
    try:
        await update.message.reply_text("מעבד את הקובץ...", quote=True)
        doc_file = await update.message.document.get_file()
        file_path = f"{doc_file.file_id}.png"
        await doc_file.download_to_drive(file_path)

        extracted_text = pytesseract.image_to_string(Image.open(file_path), lang='heb+eng')
        
        os.remove(file_path)
        
        if extracted_text.strip():
            await update.message.reply_text(extracted_text, quote=True)
        else:
            await update.message.reply_text("לא הצלחתי למצוא טקסט בקובץ.", quote=True)

    except Exception as e:
        logger.error(f"Error handling document: {e}")
        await update.message.reply_text("אירעה שגיאה בעיבוד הקובץ. ודא שזהו קובץ תמונה.")

# --- Main Application Runner ---
def main() -> None:
    """Start the bot and the keep-alive server."""
    if not TOKEN:
        logger.fatal("FATAL: BOT_TOKEN environment variable not found!")
        return

    keep_alive_thread = threading.Thread(target=run_keep_alive_server)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    application = Application.builder().token(TOKEN).build()
    
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    
    logger.info("Bot starting with Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
