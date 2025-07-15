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
PORT = int(os.environ.get("PORT", 8080))
TESSERACT_CMD_PATH = "/usr/bin/tesseract"
pytesseract.pytesseract.tesseract_cmd = TESSERACT_CMD_PATH

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
    # Use the message_id for replies
    reply_to_id = update.message.message_id
    try:
        await update.message.reply_text("מעבד את התמונה...", reply_to_message_id=reply_to_id)
        photo_file = await update.message.photo[-1].get_file()
        file_path = f"{photo_file.file_id}.jpg"
        await photo_file.download_to_drive(file_path)
        
        extracted_text = pytesseract.image_to_string(Image.open(file_path), lang='heb+eng')
        
        os.remove(file_path)
        
        if extracted_text.strip():
            await update.message.reply_text(extracted_text, reply_to_message_id=reply_to_id)
        else:
            await update.message.reply_text("לא הצלחתי למצוא טקסט בתמונה.", reply_to_message_id=reply_to_id)
            
    except Exception as e:
        logger.error(f"Exception while handling image: {e}", exc_info=True)
        await update.message.reply_text("אירעה שגיאה בעיבוד התמונה.", reply_to_message_id=reply_to_id)

async def handle_document(update: Update, context: ContextTypes.DEFAULT_TYPE) -> None:
    # This function was missing from the last version, adding it back.
    reply_to_id = update.message.message_id
    try:
        await update.message.reply_text("מעבד את הקובץ...", reply_to_message_id=reply_to_id)
        doc_file = await update.message.document.get_file()
        file_path = f"{doc_file.file_id}.png"
        await doc_file.download_to_drive(file_path)

        extracted_text = pytesseract.image_to_string(Image.open(file_path), lang='heb+eng')
        
        os.remove(file_path)
        
        if extracted_text.strip():
            await update.message.reply_text(extracted_text, reply_to_message_id=reply_to_id)
        else:
            await update.message.reply_text("לא הצלחתי למצוא טקסט בקובץ.", reply_to_message_id=reply_to_id)

    except Exception as e:
        logger.error(f"Exception while handling document: {e}", exc_info=True)
        await update.message.reply_text("אירעה שגיאה בעיבוד הקובץ. ודא שזהו קובץ תמונה.", reply_to_message_id=reply_to_id)


async def error_handler(update: object, context: ContextTypes.DEFAULT_TYPE) -> None:
    logger.error("Exception while handling an update:", exc_info=context.error)

# --- Main Application Runner ---
def main() -> None:
    if not TOKEN:
        logger.fatal("FATAL: BOT_TOKEN environment variable is missing! Application will exit.")
        exit(1)
    
    keep_alive_thread = threading.Thread(target=run_keep_alive_server)
    keep_alive_thread.daemon = True
    keep_alive_thread.start()

    application = Application.builder().token(TOKEN).build()
    
    application.add_error_handler(error_handler)
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.PHOTO, handle_image))
    application.add_handler(MessageHandler(filters.Document.IMAGE, handle_document))
    
    logger.info("Bot starting with Polling...")
    application.run_polling()

if __name__ == "__main__":
    main()
