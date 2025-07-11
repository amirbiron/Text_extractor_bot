# Telegram OCR Bot - Quick Setup Guide

## 🚀 Quick Start

### 1. Automatic Setup (Recommended)
```bash
./setup.sh
```

### 2. Get a Telegram Bot Token
1. Open Telegram and search for `@BotFather`
2. Send `/newbot` command
3. Follow the instructions to create your bot
4. Copy the token you receive

### 3. Configure the Bot
Edit the `.env` file and replace `YOUR_BOT_TOKEN_HERE` with your actual token:
```bash
nano .env
```

### 4. Run the Bot
```bash
./run.sh
```

## 📋 Manual Setup (if automatic setup fails)

### System Dependencies
```bash
sudo apt update
sudo apt install -y tesseract-ocr tesseract-ocr-heb tesseract-ocr-eng python3-venv python3-full
```

### Python Environment
```bash
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt
```

### Configuration
Copy `.env` template and edit it:
```bash
cp .env.example .env
nano .env
```

## 🤖 Bot Features

- Extract text from images (Hebrew & English)
- Support for various image formats (JPG, PNG, WEBP, etc.)
- File upload support
- Easy to use commands

## 📱 How to Use

1. Start a chat with your bot
2. Send `/start` to see the welcome message
3. Send any image to extract text from it
4. The bot will respond with the extracted text

## 🔧 Troubleshooting

### Bot Token Error
- Make sure you got the token from @BotFather
- Check that the token is correctly set in `.env` file
- Ensure there are no extra spaces or quotes

### Permission Errors
- Make sure the scripts are executable: `chmod +x *.sh`
- Run setup script with: `./setup.sh`

### Dependencies Issues
- Run setup script again: `./setup.sh`
- Check if all packages installed: `dpkg -l | grep tesseract`

## 📞 Support

If you encounter issues:
1. Check the console output for error messages
2. Verify all dependencies are installed
3. Ensure your bot token is valid
4. Make sure Telegram can reach your server (if running remotely)

## 🎯 Ready to Go!

Your Telegram OCR Bot should now be working! Send images to extract text in Hebrew and English.