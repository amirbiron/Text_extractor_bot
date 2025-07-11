import os
from dotenv import load_dotenv

# טעינת משתני סביבה מקובץ .env
load_dotenv()

class Config:
    """הגדרות הבוט"""
    
    # טוקן הבוט (חובה)
    BOT_TOKEN = os.getenv('BOT_TOKEN')
    
    # נתיב Tesseract (Windows)
    TESSERACT_PATH = os.getenv('TESSERACT_PATH')
    
    # הגדרות לוגים
    LOG_LEVEL = os.getenv('LOG_LEVEL', 'INFO')
    
    # הגדרות קבצים
    MAX_FILE_SIZE = int(os.getenv('MAX_FILE_SIZE', 20971520))  # 20MB
    
    # הגדרות OCR
    OCR_LANGUAGES = 'heb+eng'  # עברית ואנגלית
    OCR_CONFIG = r'--oem 3 --psm 6'
    
    # הגדרות Webhook (לעיצוב production)
    WEBHOOK_URL = os.getenv('WEBHOOK_URL')  # כתובת ה-webhook הציבורית
    PORT = int(os.getenv('PORT', 8080))  # פורט לשרת
    
    # הודעות
    WELCOME_MESSAGE = """
🤖 ברוכים הבאים לבוט חילוץ טקסט מתמונות!

📸 שלחו לי תמונה ואני אחלץ את הטקסט שבתוכה
🔤 הבוט תומך בעברית ובאנגלית
📄 אפשר לשלוח תמונות כקובץ או כתמונה רגילה

📋 פקודות זמינות:
/start - הודעת פתיחה
/help - עזרה ומידע נוסף

פשוט שלחו תמונה והתחילו! 🚀
    """
    
    HELP_MESSAGE = """
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
    
    @classmethod
    def validate(cls):
        """בדיקת תקינות ההגדרות"""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required. Please set it in .env file")
        
        # אזהרה אם WEBHOOK_URL לא מוגדר (אבל לא הפסקה)
        if not cls.WEBHOOK_URL:
            print("⚠️  WEBHOOK_URL is not set. This is required for production deployment.")
        
        return True
