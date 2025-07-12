import subprocess
import time
import logging

# Basic logging to see output clearly in Render's logs
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(message)s')
logger = logging.getLogger(__name__)

logger.info("--- Starting Diagnostic Script ---")

# Test 1: Try to find where tesseract is using 'whereis'
logger.info("--- Running 'whereis tesseract' ---")
try:
    result = subprocess.run(['whereis', 'tesseract'], capture_output=True, text=True, check=False)
    logger.info(f"Stdout: {result.stdout.strip()}")
    logger.info(f"Stderr: {result.stderr.strip()}")
except FileNotFoundError:
    logger.error("'whereis' command not found. This is unusual for the base image.")
except Exception as e:
    logger.error(f"Failed to run 'whereis': {e}")

# Test 2: Check if the file exists at the expected path using 'ls'
logger.info("\n--- Running 'ls -l /usr/bin/tesseract' ---")
try:
    result = subprocess.run(['ls', '-l', '/usr/bin/tesseract'], capture_output=True, text=True, check=False)
    if result.returncode == 0:
        logger.info(f"File found! Details: {result.stdout.strip()}")
    else:
        logger.error(f"File not found at /usr/bin/tesseract. Stderr: {result.stderr.strip()}")
except FileNotFoundError:
    logger.error("'ls' command not found. This is highly unusual.")
except Exception as e:
    logger.error(f"Failed to run 'ls': {e}")

logger.info("\n--- Diagnostic Script Finished. Idling to allow log inspection. ---")

# Keep the script running for a few minutes so we can read the logs
time.sleep(300)
