# פתרון שגיאות הבוט - Troubleshooting Guide

## השגיאות שזוהו והפתרונות

### 1. שגיאת Telegram Conflict
**שגיאה:** `telegram.error.Conflict: Conflict: terminated by other getUpdates request`

**סיבה:** מריצים יותר מאובייקט בוט אחד בו זמנית עם אותו טוקן.

**פתרון:** 
- וודאו שרק מופע אחד של הבוט רץ
- השתמשו בפקודה `pkill -f "python.*bot"` לעצירת כל הבוטים
- הריצו רק מופע אחד

### 2. שגיאת Port Binding
**שגיאה:** `Port scan timeout reached, no open ports detected`

**סיבה:** סביבת הפריסה מצפה שהשירות יתחבר לפורט.

**פתרון:** 
- נוצר קובץ `web_bot.py` שמפעיל גם שרת HTTP
- השרת רץ על פורט 8080 (או PORT environment variable)
- מספק endpoint `/health` לבדיקת תקינות

### 3. חסרים Dependencies
**שגיאה:** חבילות Python חסרות

**פתרון:**
- הותקן Tesseract OCR עם תמיכה בעברית
- נוצר virtual environment
- הותקנו כל החבילות הנדרשות

### 4. חסר קובץ .env
**שגיאה:** `BOT_TOKEN is required`

**פתרון:**
- נוצר קובץ `.env` עם template
- צריך להזין את הטוקן מ-@BotFather

## איך להפעיל את הבוט

### 1. הגדרת הטוקן
ערכו את הקובץ `.env` והחליפו `YOUR_BOT_TOKEN_HERE` בטוקן האמיתי:

```bash
BOT_TOKEN=1234567890:ABCdefGHIjklMNOpqrSTUvwxyz
```

### 2. הפעלת הבוט עם שרת web (מומלץ)
```bash
source venv/bin/activate
python web_bot.py
```

### 3. הפעלת הבוט רגיל (בלי שרת web)
```bash
source venv/bin/activate
python bot.py
```

## בדיקת תקינות

### בדיקת הבוט בטלגרם
1. שלחו `/start` לבוט
2. שלחו תמונה עם טקסט
3. הבוט אמור לחזור עם הטקסט שחולץ

### בדיקת שרת ה-Web
```bash
curl http://localhost:8080/health
```
תקבלו: `OK - Bot is running`

## פקודות שימושיות

### עצירת כל הבוטים
```bash
pkill -f "python.*bot"
```

### בדיקת פרוצסים פעילים
```bash
ps aux | grep python
```

### בדיקת תקינות Tesseract
```bash
tesseract --version
```

### הפעלת הבוט ברקע
```bash
nohup python web_bot.py &
```

## פתרון בעיות נוספות

### אם הבוט לא מגיב
1. בדקו שהטוקן נכון
2. בדקו שיש חיבור לאינטרנט
3. בדקו שרק מופע אחד רץ

### אם OCR לא עובד
1. בדקו שTesseract מותקן: `which tesseract`
2. בדקו שהתמונה ברורה
3. בדקו שתמיכה בעברית מותקנת

### אם השרת לא מתחיל
1. בדקו שהפורט פנוי
2. השתמשו בפורט אחר: `PORT=8081 python web_bot.py`
3. בדקו את הלוגים לשגיאות

## קבצים חשובים

- `bot.py` - הבוט המקורי (polling בלבד)
- `web_bot.py` - בוט עם שרת web (מומלץ)
- `config.py` - הגדרות הבוט
- `.env` - משתני סביבה (טוקן הבוט)
- `requirements.txt` - חבילות Python נדרשות

## הערות חשובות

1. **אל תשתפו את הטוקן** - שמרו אותו בסוד
2. **הריצו רק מופע אחד** - יותר מאחד יגרום לשגיאות
3. **השתמשו ב-virtual environment** - למניעת קונפליקטים
4. **בדקו תקינות Tesseract** - נדרש לפונקציונליות OCR