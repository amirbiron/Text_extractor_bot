import os
import logging
import time

# --- Verbose Diagnostic Block at the very top ---
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(levelname)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- Starting Final Diagnostic Check ---")

# Print all available environment variables to find any typos or issues
logger.info("--- All available environment variables: ---")
all_vars = os.environ.items()
if not all_vars:
    logger.info("No environment variables found.")
else:
    for key, value in all_vars:
        # Mask sensitive values for security in logs
        if "TOKEN" in key.upper() or "KEY" in key.upper() or "URI" in key.upper():
            value = f"***...{value[-4:]}" if len(value) > 8 else "***"
        logger.info(f"'{key}': '{value}'")
logger.info("-----------------------------------------")


# Check for the specific variables we need
bot_token = os.environ.get("BOT_TOKEN")
tesseract_cmd = os.environ.get("TESSERACT_CMD")

logger.info(f"Attempting to read BOT_TOKEN. Found: {'Yes' if bot_token else 'No'}")
logger.info(f"Attempting to read TESSERACT_CMD. Found: {'Yes' if tesseract_cmd else 'No'}")


if not bot_token:
    logger.error("FATAL: BOT_TOKEN is missing or empty. Bot cannot start.")
    logger.info("Container will idle for 5 minutes for inspection before exiting.")
    time.sleep(300)
    exit(1)
else:
    logger.info("SUCCESS: BOT_TOKEN was found. The bot should be able to start.")
    logger.info("Container will now exit as this was a diagnostic run.")
    time.sleep(5)
