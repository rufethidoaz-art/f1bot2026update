"""
Webhook info endpoint for Vercel
"""

import os
import json
from http import HTTPStatus
from datetime import datetime

def get_webhook_url():
    return os.getenv("WEBHOOK_URL", "NOT_SET")

async def default(event, context):
    """Webhook info endpoint"""
    return {
        'statusCode': HTTPStatus.OK,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            "webhook_url": get_webhook_url(),
            "bot_initialized": False,  # Will be managed globally in production
            "timestamp": datetime.now().isoformat()
        })
    }