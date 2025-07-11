# Deployment Guide for Telegram OCR Bot

## Problem Resolution

The issues you encountered were:

1. **Telegram Bot Conflict**: Multiple bot instances using polling (`getUpdates`) were running simultaneously
2. **Port Binding Issue**: Render.com requires proper port binding for web services

## Solution

We've created a webhook-based bot (`webhook_bot.py`) that resolves both issues:

- Uses webhooks instead of polling (eliminates conflicts)
- Properly binds to a port for Render.com deployment
- Includes health check endpoints

## Deployment Steps

### 1. Environment Variables

Set these environment variables in your Render.com dashboard:

```bash
BOT_TOKEN=your_telegram_bot_token_here
WEBHOOK_URL=https://your-render-app-name.onrender.com
PORT=8080
LOG_LEVEL=INFO
```

### 2. Update Build Command

In Render.com, set your build command to:

```bash
pip install --upgrade pip && pip install -r requirements.txt
```

### 3. Update Start Command

In Render.com, set your start command to:

```bash
python deploy.py
```

### 4. Stop Other Bot Instances

**IMPORTANT**: Make sure to stop any other bot instances that might be running with polling:

- Stop any local `bot.py` instances
- Stop any other `web_bot.py` instances
- Only run the webhook bot (`webhook_bot.py` via `deploy.py`)

### 5. Verify Deployment

After deployment, you can verify the bot is working:

1. Check health endpoint: `https://your-app-name.onrender.com/health`
2. Check status endpoint: `https://your-app-name.onrender.com/`
3. Test the bot in Telegram

## Files Overview

- `webhook_bot.py` - Main webhook-based bot (production)
- `deploy.py` - Deployment script for Render.com
- `bot.py` - Local polling bot (development only)
- `web_bot.py` - Old version (deprecated)

## Configuration

The webhook bot automatically:

- Sets up the webhook URL with Telegram API
- Binds to the specified port
- Provides health check endpoints
- Processes updates via HTTP POST requests

## Troubleshooting

### Still Getting Conflicts?

1. Check that only one bot instance is running
2. Verify the webhook URL is correct
3. Look for any background processes still running the polling bot

### Port Issues?

1. Ensure `PORT` environment variable is set
2. Verify Render.com service type is set to "Web Service"
3. Check that the bot binds to `0.0.0.0:PORT`

### Webhook Not Working?

1. Verify `WEBHOOK_URL` matches your Render.com URL
2. Check that the URL is accessible from the internet
3. Ensure SSL/TLS is enabled (Render.com provides this automatically)

## Migration from Polling to Webhook

If you're migrating from polling to webhook:

1. Stop the polling bot
2. Deploy the webhook bot
3. The webhook bot will automatically register the webhook URL
4. Test that the bot responds to messages

## Local Development

For local development, you can still use the polling bot:

```bash
python bot.py
```

For production, always use the webhook bot:

```bash
python deploy.py
```