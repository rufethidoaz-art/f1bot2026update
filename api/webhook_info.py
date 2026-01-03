"""
Webhook info endpoint for Vercel
"""

import os
import json
from http import HTTPStatus
from datetime import datetime

def get_webhook_url():
    return os.getenv("WEBHOOK_URL", "NOT_SET")

def handler(event, context):
    """Webhook info endpoint - Vercel serverless function"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            "webhook_url": get_webhook_url(),
            "bot_initialized": False,
            "timestamp": datetime.now().isoformat()
        })
    }

# Vercel compatibility
app = handler