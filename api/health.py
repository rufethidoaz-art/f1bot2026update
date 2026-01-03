"""
Health check endpoint for Vercel
"""

import os
import json
from http import HTTPStatus
from datetime import datetime

def get_webhook_url():
    return os.getenv("WEBHOOK_URL", "Not set")

def get_bot_token():
    return "SET" if os.getenv("TELEGRAM_BOT_TOKEN") else "NOT_SET"

async def default(event, context):
    """Health check endpoint"""
    return {
        'statusCode': HTTPStatus.OK,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            "status": "healthy",
            "service": "F1 Telegram Bot",
            "timestamp": datetime.now().isoformat(),
            "webhook_url": get_webhook_url(),
            "bot_token": get_bot_token(),
            "version": "2.0.0"
        })
    }