#!/bin/bash
# Script to run the Telegram OCR Bot

echo "🤖 Starting Telegram OCR Bot..."

# Check if virtual environment exists
if [ ! -d "venv" ]; then
    echo "❌ Virtual environment not found. Please run setup.sh first."
    exit 1
fi

# Check if .env file exists and has BOT_TOKEN
if [ ! -f ".env" ]; then
    echo "❌ .env file not found. Please create it and add your BOT_TOKEN."
    exit 1
fi

# Check if BOT_TOKEN is set
if grep -q "BOT_TOKEN=YOUR_BOT_TOKEN_HERE" .env; then
    echo "❌ BOT_TOKEN is not set in .env file."
    echo "Please get your bot token from @BotFather on Telegram and add it to .env:"
    echo "BOT_TOKEN=your_actual_token_here"
    exit 1
fi

# Activate virtual environment and run the bot
source venv/bin/activate
python3 bot.py