"""
Health check endpoint for Vercel
"""

import os
import json
from datetime import datetime

def handler(event, context):
    """Health check endpoint - Vercel serverless function"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            "status": "healthy",
            "service": "F1 Telegram Bot",
            "timestamp": datetime.now().isoformat(),
            "webhook_url": os.getenv("WEBHOOK_URL", "Not set"),
            "bot_token": "SET" if os.getenv("TELEGRAM_BOT_TOKEN") else "NOT_SET",
            "version": "2.0.0"
        })
    }

# Vercel compatibility
app = handler