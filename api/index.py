"""
Main index endpoint for Vercel - Fixed format
"""

import json
from datetime import datetime

def handler(event, context):
    """Vercel serverless function"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            "status": "F1 Telegram Bot is running!",
            "version": "2.0.0",
            "deployment": "Vercel",
            "timestamp": datetime.now().isoformat()
        })
    }

# Vercel compatibility
app = handler