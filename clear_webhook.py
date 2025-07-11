#!/usr/bin/env python3
"""
Utility script to clear existing webhooks and resolve bot conflicts
Run this script if you're experiencing webhook conflicts
"""

import asyncio
import requests
import logging
from config import Config

# הגדרת לוגים
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

def clear_webhook_sync(bot_token: str):
    """ביטול webhook בצורה סינכרונית"""
    try:
        # ביטול webhook
        url = f"https://api.telegram.org/bot{bot_token}/deleteWebhook"
        response = requests.post(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                logger.info("✅ Webhook cleared successfully")
                return True
            else:
                logger.error(f"❌ Failed to clear webhook: {result.get('description')}")
                return False
        else:
            logger.error(f"❌ HTTP Error: {response.status_code}")
            return False
            
    except Exception as e:
        logger.error(f"❌ Error clearing webhook: {e}")
        return False

def get_webhook_info(bot_token: str):
    """קבלת מידע על ה-webhook הנוכחי"""
    try:
        url = f"https://api.telegram.org/bot{bot_token}/getWebhookInfo"
        response = requests.get(url)
        
        if response.status_code == 200:
            result = response.json()
            if result.get('ok'):
                webhook_info = result.get('result', {})
                logger.info("📋 Current webhook info:")
                logger.info(f"   URL: {webhook_info.get('url', 'None')}")
                logger.info(f"   Has custom certificate: {webhook_info.get('has_custom_certificate', False)}")
                logger.info(f"   Pending update count: {webhook_info.get('pending_update_count', 0)}")
                logger.info(f"   Last error date: {webhook_info.get('last_error_date', 'None')}")
                logger.info(f"   Last error message: {webhook_info.get('last_error_message', 'None')}")
                return webhook_info
            else:
                logger.error(f"❌ Failed to get webhook info: {result.get('description')}")
                return None
        else:
            logger.error(f"❌ HTTP Error: {response.status_code}")
            return None
            
    except Exception as e:
        logger.error(f"❌ Error getting webhook info: {e}")
        return None

def main():
    """פונקציה ראשית"""
    logger.info("🔧 Telegram Bot Webhook Cleaner")
    logger.info("================================")
    
    try:
        # בדיקת הגדרות
        Config.validate()
        
        # הצגת מידע על webhook נוכחי
        logger.info("📋 Checking current webhook status...")
        webhook_info = get_webhook_info(Config.BOT_TOKEN)
        
        if webhook_info and webhook_info.get('url'):
            logger.info("🔗 Webhook is currently set")
            logger.info("🧹 Clearing webhook...")
            
            if clear_webhook_sync(Config.BOT_TOKEN):
                logger.info("✅ Webhook cleared successfully!")
                logger.info("✅ Bot conflicts should now be resolved")
                logger.info("📝 You can now deploy your webhook bot")
            else:
                logger.error("❌ Failed to clear webhook")
                return False
        else:
            logger.info("✅ No webhook is currently set")
            logger.info("✅ No conflicts detected")
        
        # בדיקה חוזרת
        logger.info("🔍 Verifying webhook status...")
        final_info = get_webhook_info(Config.BOT_TOKEN)
        
        if final_info and not final_info.get('url'):
            logger.info("✅ Webhook successfully removed")
            logger.info("🚀 Ready for new deployment!")
        else:
            logger.warning("⚠️  Webhook might still be active")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)