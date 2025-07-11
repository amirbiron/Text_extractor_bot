import logging
import os
import io
import json
from flask import Flask, request, jsonify
from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import pytesseract
import requests
from config import Config
import asyncio
import threading

# בדיקת תקינות ההגדרות
Config.validate()

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=getattr(logging, Config.LOG_LEVEL)
)
logger = logging.getLogger(__name__)

# הגדרת נתיב Tesseract (עבור Windows)
if Config.TESSERACT_PATH:
    pytesseract.pytesseract.tesseract_cmd = Config.TESSERACT_PATH

# Flask app for webhook
app = Flask(__name__)

class TelegramOCRBot:
    def __init__(self, token: str, webhook_url: str = None):
        self.token = token
        self.webhook_url = webhook_url
        self.application = Application.builder().token(token).build()
        self.setup_handlers()
    
    def setup_handlers(self):
        """הגדרת handlers עבור הבוט"""
        self.application.add_handler(CommandHandler("start", self.start))
        self.application.add_handler(CommandHandler("help", self.help))
        self.application.add_handler(MessageHandler(filters.PHOTO, self.handle_photo))
        self.application.add_handler(MessageHandler(filters.Document.IMAGE, self.handle_document))
        self.application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, self.handle_text))
    
    async def start(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """פונקציית התחלה"""
        await update.message.reply_text(Config.WELCOME_MESSAGE)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """פונקציית עזרה"""
        await update.message.reply_text(Config.HELP_MESSAGE)
    
    async def handle_photo(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בתמונה שנשלחה"""
        try:
            # שליחת הודעת טעינה
            loading_msg = await update.message.reply_text("🔄 מעבד את התמונה...")
            
            # הורדת התמונה
            photo = update.message.photo[-1]  # התמונה באיכות הגבוהה ביותר
            file = await context.bot.get_file(photo.file_id)
            
            # הורדת התמונה
            image_bytes = await self.download_image(file.file_path)
            
            # חילוץ טקסט
            text = await self.extract_text_from_image(image_bytes)
            
            # מחיקת הודעת הטעינה
            await loading_msg.delete()
            
            # שליחת התוצאה
            if text.strip():
                response = f"📝 **הטקסט שנמצא בתמונה:**\n\n{text}"
                await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ לא נמצא טקסט בתמונה או שהטקסט לא ברור מספיק")
                
        except Exception as e:
            logger.error(f"שגיאה בעיבוד תמונה: {e}")
            await update.message.reply_text("❌ אירעה שגיאה בעיבוד התמונה. אנא נסו שנית.")
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בתמונה שנשלחה כקובץ"""
        try:
            document = update.message.document
            
            # בדיקה שזה קובץ תמונה
            if not document.mime_type.startswith('image/'):
                await update.message.reply_text("❌ אנא שלחו קובץ תמונה בלבד")
                return
            
            # שליחת הודעת טעינה
            loading_msg = await update.message.reply_text("🔄 מעבד את התמונה...")
            
            # הורדת הקובץ
            file = await context.bot.get_file(document.file_id)
            image_bytes = await self.download_image(file.file_path)
            
            # חילוץ טקסט
            text = await self.extract_text_from_image(image_bytes)
            
            # מחיקת הודעת הטעינה
            await loading_msg.delete()
            
            # שליחת התוצאה
            if text.strip():
                response = f"📝 **הטקסט שנמצא בתמונה:**\n\n{text}"
                await update.message.reply_text(response, parse_mode='Markdown')
            else:
                await update.message.reply_text("❌ לא נמצא טקסט בתמונה או שהטקסט לא ברור מספיק")
                
        except Exception as e:
            logger.error(f"שגיאה בעיבוד קובץ: {e}")
            await update.message.reply_text("❌ אירעה שגיאה בעיבוד הקובץ. אנא נסו שנית.")
    
    async def handle_text(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """טיפול בהודעות טקסט"""
        await update.message.reply_text(
            "📸 אנא שלחו תמונה כדי לחלץ ממנה טקסט!\n\n"
            "ניתן לשלוח תמונה בתור:\n"
            "• תמונה רגילה\n"
            "• קובץ תמונה\n\n"
            "השתמשו ב-/help למידע נוסף"
        )
    
    async def download_image(self, file_path: str) -> bytes:
        """הורדת תמונה מטלגרם"""
        url = f"https://api.telegram.org/file/bot{self.token}/{file_path}"
        response = requests.get(url)
        response.raise_for_status()
        return response.content
    
    async def extract_text_from_image(self, image_bytes: bytes) -> str:
        """חילוץ טקסט מתמונה באמצעות OCR"""
        try:
            # פתיחת התמונה
            image = Image.open(io.BytesIO(image_bytes))
            
            # המרה ל-RGB אם צריך
            if image.mode != 'RGB':
                image = image.convert('RGB')
            
            # חילוץ טקסט עם תמיכה בעברית ובאנגלית
            custom_config = f'{Config.OCR_CONFIG} -l {Config.OCR_LANGUAGES}'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"שגיאה בחילוץ טקסט: {e}")
            raise
    
    async def process_update(self, update_data: dict):
        """עיבוד עדכון מהwebhook"""
        try:
            update = Update.de_json(update_data, self.application.bot)
            await self.application.process_update(update)
        except Exception as e:
            logger.error(f"שגיאה בעיבוד עדכון: {e}")
    
    async def setup_webhook(self):
        """הגדרת webhook"""
        if self.webhook_url:
            try:
                await self.application.bot.set_webhook(
                    url=f"{self.webhook_url}/webhook",
                    allowed_updates=["message", "callback_query"]
                )
                logger.info(f"Webhook set to: {self.webhook_url}/webhook")
            except Exception as e:
                logger.error(f"Failed to set webhook: {e}")
    
    async def initialize(self):
        """אתחול הבוט"""
        await self.application.initialize()
        await self.setup_webhook()

# יצירת instance של הבוט
bot_instance = None

async def init_bot():
    """אתחול הבוט"""
    global bot_instance
    # Fallback: if WEBHOOK_URL not explicitly set, try building it from Render's external hostname
    webhook_url = os.getenv('WEBHOOK_URL')
    if not webhook_url:
        render_host = os.getenv("RENDER_EXTERNAL_HOSTNAME")
        if render_host:
            webhook_url = f"https://{render_host}"
            logger.info(f"Derived WEBHOOK_URL from RENDER_EXTERNAL_HOSTNAME: {webhook_url}")

    bot_instance = TelegramOCRBot(Config.BOT_TOKEN, webhook_url)
    await bot_instance.initialize()

# Flask routes
@app.route('/health', methods=['GET'])
def health_check():
    """בדיקת תקינות השירות"""
    return jsonify({"status": "OK", "message": "Bot is running"}), 200

@app.route('/webhook', methods=['POST'])
def webhook():
    """קבלת עדכונים מטלגרם"""
    if request.method == 'POST':
        update_data = request.get_json()
        if update_data and bot_instance:
            # עיבוד העדכון בthread נפרד
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            loop.run_until_complete(bot_instance.process_update(update_data))
            loop.close()
        return jsonify({"status": "OK"}), 200
    return jsonify({"status": "Method not allowed"}), 405

@app.route('/', methods=['GET'])
def index():
    """דף הבית"""
    return jsonify({
        "message": "Telegram OCR Bot is running",
        "status": "active",
        "endpoints": {
            "health": "/health",
            "webhook": "/webhook"
        }
    }), 200

def run_flask_app():
    """הרצת Flask app"""
    port = int(os.getenv('PORT', 8080))
    app.run(host='0.0.0.0', port=port, debug=False)

def main():
    """פונקציה ראשית"""
    print("🤖 Starting Telegram OCR Bot with webhook...")
    
    # אתחול הבוט
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)
    loop.run_until_complete(init_bot())
    
    # הרצת Flask app
    run_flask_app()

if __name__ == "__main__":
    main()