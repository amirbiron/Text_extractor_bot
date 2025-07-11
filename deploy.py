#!/usr/bin/env python3
"""
Deployment script for Telegram OCR Bot
Uses webhook for production deployment on Render.com
"""

import os
import sys
import logging
from webhook_bot import main as webhook_main
from config import Config

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def main():
    """הפעלת הבוט במצב production"""
    logger.info("🚀 Starting bot deployment...")
    
    try:
        # בדיקת הגדרות
        Config.validate()
        
        # הדפסת מידע על הפעלה
        port = Config.PORT
        webhook_url = Config.WEBHOOK_URL
        
        logger.info(f"📡 Starting webhook bot on port {port}")
        if webhook_url:
            logger.info(f"🔗 Webhook URL: {webhook_url}")
        else:
            logger.warning("⚠️  No webhook URL configured - bot will run in development mode")
        
        # הפעלת הבוט
        webhook_main()
        
    except Exception as e:
        logger.error(f"❌ Failed to start bot: {e}")
        sys.exit(1)

if __name__ == "__main__":
    main()