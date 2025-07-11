#!/bin/bash
# Setup script for Telegram OCR Bot

echo "🔧 Setting up Telegram OCR Bot..."

# Check if we're on Ubuntu/Debian
if ! command -v apt &> /dev/null; then
    echo "❌ This script is designed for Ubuntu/Debian systems with apt package manager."
    exit 1
fi

# Install system dependencies
echo "📦 Installing system dependencies..."
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng python3-venv python3-full

# Create virtual environment if it doesn't exist
if [ ! -d "venv" ]; then
    echo "🐍 Creating Python virtual environment..."
    python3 -m venv venv
fi

# Install Python dependencies
echo "📚 Installing Python dependencies..."
source venv/bin/activate
pip install --upgrade pip
pip install -r requirements.txt

# Create .env file if it doesn't exist
if [ ! -f ".env" ]; then
    echo "⚙️ Creating .env configuration file..."
    cat > .env << EOF
# Telegram Bot Configuration
# Get your bot token from @BotFather on Telegram
BOT_TOKEN=YOUR_BOT_TOKEN_HERE

# Optional: Path to Tesseract (usually not needed on Linux)
# TESSERACT_PATH=/usr/bin/tesseract

# Log level (DEBUG, INFO, WARNING, ERROR)
LOG_LEVEL=INFO

# Maximum file size in bytes (20MB default)
MAX_FILE_SIZE=20971520
EOF
fi

echo "✅ Setup complete!"
echo ""
echo "📋 Next steps:"
echo "1. Get a bot token from @BotFather on Telegram"
echo "2. Edit .env file and replace YOUR_BOT_TOKEN_HERE with your actual token"
echo "3. Run the bot with: ./run.sh"
echo ""
echo "📖 For more information, check README.md"