"""
Simple health check endpoint
"""

import json
import os
from datetime import datetime

def handler(event, context):
    """Simple health check"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': json.dumps({
            "status": "healthy",
            "timestamp": datetime.now().isoformat(),
            "token_set": bool(os.getenv("TELEGRAM_BOT_TOKEN"))
        })
    }

app = handler