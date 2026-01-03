"""
Set webhook endpoint for Vercel
"""

import os
import json
import sys
import asyncio
from http import HTTPStatus

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Bot

def get_bot_token():
    return os.getenv("TELEGRAM_BOT_TOKEN")

def get_webhook_url():
    return os.getenv("WEBHOOK_URL", "")

async def set_webhook_manually(webhook_url):
    """Manually set webhook URL"""
    token = get_bot_token()
    if not token:
        return False
    
    try:
        bot = Bot(token=token)
        result = await bot.set_webhook(url=webhook_url)
        return result
    except Exception as e:
        print(f"Error setting webhook: {e}")
        return False

def handler(event, context):
    """Set webhook endpoint - Vercel serverless function"""
    import asyncio
    
    webhook_url = get_webhook_url()
    
    if not webhook_url:
        return {
            'statusCode': HTTPStatus.BAD_REQUEST,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "error",
                "message": "WEBHOOK_URL environment variable not set"
            })
        }
    
    try:
        success = asyncio.run(set_webhook_manually(webhook_url))
        if success:
            return {
                'statusCode': HTTPStatus.OK,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    "status": "success",
                    "webhook_url": webhook_url,
                    "message": "Webhook set successfully"
                })
            }
        else:
            return {
                'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
                'headers': {'Content-Type': 'application/json'},
                'body': json.dumps({
                    "status": "error",
                    "message": "Failed to set webhook"
                })
            }
    except Exception as e:
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'headers': {'Content-Type': 'application/json'},
            'body': json.dumps({
                "status": "error",
                "message": str(e)
            })
        }