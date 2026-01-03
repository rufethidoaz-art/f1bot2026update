"""
Main index endpoint for Vercel
"""

import json
from http import HTTPStatus
from datetime import datetime

async def default(event, context):
    """Main endpoint"""
    return {
        'statusCode': HTTPStatus.OK,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            "status": "F1 Telegram Bot is running!",
            "version": "2.0.0",
            "deployment": "Vercel",
            "timestamp": datetime.now().isoformat(),
            "endpoints": {
                "webhook": "/webhook",
                "health": "/health",
                "debug": "/debug",
                "webhook_info": "/webhook-info",
                "set_webhook": "/set-webhook"
            }
        })
    }