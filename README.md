# Telegram OCR Bot / בוט טלגרם לחילוץ טקסט מתמונות

🤖 בוט טלגרם המחלץ טקסט מתמונות באמצעות טכנולוגיית OCR עם תמיכה מלאה בעברית ובאנגלית.

A Telegram bot that extracts text from images using OCR technology with full Hebrew and English support.

## ✨ תכונות / Features

- 🔤 חילוץ טקסט מתמונות בעברית ובאנגלית / Extract text from images in Hebrew and English
- 📸 תמיכה בתמונות רגילות וקבצים / Support for regular photos and document files  
- 🎯 ממשק ידידותי בעברית / User-friendly Hebrew interface
- ⚡ עיבוד מהיר ויעיל / Fast and efficient processing
- 🔧 טיפול חכם בשגיאות / Smart error handling

## 📋 דרישות מערכת / System Requirements

- Python 3.8+
- Tesseract OCR
- חיבור לאינטרנט / Internet connection

## 🚀 התקנה / Installation

### שלב 1: שכפול הפרויקט / Clone the project
```bash
git clone https://github.com/yourusername/telegram-ocr-bot.git
cd telegram-ocr-bot
```

### שלב 2: התקנת Tesseract OCR
**Windows:**
1. הורידו מ-[GitHub Releases](https://github.com/UB-Mannheim/tesseract/wiki)
2. התקינו והוסיפו לנתיב המערכת (PATH)

**macOS:**
```bash
brew install tesseract
```

**Ubuntu/Debian:**
```bash
sudo apt-get update
sudo apt-get install tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng
```

### שלב 3: יצירת בוט טלגרם / Create Telegram Bot
1. פתחו שיחה עם [@BotFather](https://t.me/BotFather)
2. שלחו `/newbot`
3. בחרו שם לבוט (לדוגמה: "OCR Text Extractor")
4. בחרו username (לדוגמה: "my_ocr_bot")
5. שמרו את ה-token שתקבלו

### שלב 4: הגדרת הפרויקט / Project Setup
```bash
# יצירת סביבה וירטואלית
python -m venv venv

# הפעלת הסביבה הוירטואלית
# Windows:
venv\Scripts\activate
# macOS/Linux:
source venv/bin/activate

# התקנת תלויות
pip install -r requirements.txt
```

### שלב 5: הגדרת משתני סביבה / Environment Setup
1. העתיקו את קובץ `.env.example` ל-`.env`
2. ערכו את הקובץ `.env` והכניסו את token הבוט:
```
BOT_TOKEN=YOUR_ACTUAL_BOT_TOKEN_HERE
```

### שלב 6: הפעלת הבוט / Run the Bot
```bash
python bot.py
```

## 🔧 שימוש / Usage

1. התחילו שיחה עם הבוט שיצרתם
2. שלחו `/start` להתחלה
3. שלחו תמונה (כתמונה רגילה או כקובץ)
4. קבלו את הטקסט שחולץ מהתמונה

## 📁 מבנה הפרויקט / Project Structure

```
telegram-ocr-bot/
├── bot.py              # קוד הבוט הראשי / Main bot code
├── requirements.txt    # תלויות Python / Python dependencies
├── README.md          # תיעוד / Documentation
├── .env.example       # דוגמה למשתני סביבה / Environment variables example
├── .gitignore         # קבצים להתעלמות / Git ignore file
└── config.py          # הגדרות (אופציונלי) / Configuration (optional)
```

## 📝 פקודות זמינות / Available Commands

- `/start` - הודעת ברוכים הבאים / Welcome message
- `/help` - מידע ועזרה / Help and information

## 🐛 פתרון בעיות / Troubleshooting

### שגיאות נפוצות / Common Errors

**"Tesseract not found":**
- ודאו שהתקנתם את Tesseract OCR
- ב-Windows: ודאו שהנתיב נוסף ל-PATH או הסירו הערה מהשורה בקוד

**"Invalid token":**
- ודאו שהכנסתם את הטוקן הנכון בקובץ `.env`

**"No text found":**
- נסו תמונה עם טקסט ברור יותר
- ודאו שהטקסט בתמונה בעברית או באנגלית

## 🤝 תרומה / Contributing

מוזמנים לתרום לפרויקט! פתחו Issues או Pull Requests.

## 📄 רישיון / License

MIT License - ראו קובץ LICENSE לפרטים מלאים

## 👨‍💻 יוצר / Author

[השם שלכם] - [הדוא"ל שלכם]

---

⭐ אם הפרויקט עזר לכם, אל תשכחו לתת כוכב ב-GitHub!
