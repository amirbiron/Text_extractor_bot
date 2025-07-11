import logging
import os
import io
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
from PIL import Image
import pytesseract
import requests

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# הגדרת נתיב Tesseract (עבור Windows)
# pytesseract.pytesseract.tesseract_cmd = r'C:\Program Files\Tesseract-OCR\tesseract.exe'

class TelegramOCRBot:
    def __init__(self, token: str):
        self.token = token
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
        welcome_text = """
🤖 ברוכים הבאים לבוט חילוץ טקסט מתמונות!

📸 שלחו לי תמונה ואני אחלץ את הטקסט שבתוכה
🔤 הבוט תומך בעברית ובאנגלית
📄 אפשר לשלוח תמונות כקובץ או כתמונה רגילה

📋 פקודות זמינות:
/start - הודעת פתיחה
/help - עזרה ומידע נוסף

פשוט שלחו תמונה והתחילו! 🚀
        """
        await update.message.reply_text(welcome_text)
    
    async def help(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """פונקציית עזרה"""
        help_text = """
📖 איך להשתמש בבוט:

1️⃣ שלחו תמונה (כתמונה רגילה או כקובץ)
2️⃣ חכו שהבוט יעבד את התמונה
3️⃣ תקבלו את הטקסט שנמצא בתמונה

💡 טיפים:
• תמונות ברורות יותר נותנות תוצאות טובות יותר
• טקסט גדול וברור יחולץ טוב יותר
• הבוט תומך בעברית ובאנגלית

🔧 פורמטים נתמכים:
• JPG, PNG, WEBP, BMP, GIF
• תמונות שנשלחו כקובץ או כתמונה
        """
        await update.message.reply_text(help_text)
    
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
            # הגדרת שפות: עברית (heb) ואנגלית (eng)
            custom_config = r'--oem 3 --psm 6 -l heb+eng'
            text = pytesseract.image_to_string(image, config=custom_config)
            
            return text.strip()
            
        except Exception as e:
            logger.error(f"שגיאה בחילוץ טקסט: {e}")
            raise
    
    def run(self):
        """הפעלת הבוט"""
        print("🤖 הבוט מופעל...")
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)

# פונקציה ראשית
def main():
    # כאן תחליפו את המפתח שלכם
    BOT_TOKEN = "YOUR_BOT_TOKEN_HERE"
    
    if BOT_TOKEN == "YOUR_BOT_TOKEN_HERE":
        print("❌ אנא החליפו את BOT_TOKEN במפתח הבוט שלכם")
        return
    
    # יצירת והפעלת הבוט
    bot = TelegramOCRBot(BOT_TOKEN)
    bot.run()

if __name__ == "__main__":
    main()
