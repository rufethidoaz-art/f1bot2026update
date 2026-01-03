"""
Debug endpoint for Vercel
"""

import os
import json
import sys
from http import HTTPStatus
from datetime import datetime

# Add parent directory to path
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def get_bot_token():
    return os.getenv("TELEGRAM_BOT_TOKEN")

def get_webhook_url():
    return os.getenv("WEBHOOK_URL", "NOT_SET")

async def default(event, context):
    """Debug endpoint"""
    import_status = {}
    
    try:
        from f1_bot_live import start, get_current_standings
        import_status["f1_bot_live"] = "OK"
    except Exception as e:
        import_status["f1_bot_live"] = f"ERROR: {str(e)}"
    
    try:
        import telegram
        import_status["telegram"] = f"OK (v{telegram.__version__})"
    except Exception as e:
        import_status["telegram"] = f"ERROR: {str(e)}"
    
    try:
        import playwright
        try:
            import_status["playwright"] = f"OK (v{playwright.__version__})"
        except AttributeError:
            import_status["playwright"] = "OK (version unknown)"
    except Exception as e:
        import_status["playwright"] = f"ERROR: {str(e)}"
    
    return {
        'statusCode': HTTPStatus.OK,
        'headers': {
            'Content-Type': 'application/json',
        },
        'body': json.dumps({
            "bot_token_set": bool(get_bot_token()),
            "version": "2.0.0",
            "imports": import_status,
            "python_version": f"{sys.version_info.major}.{sys.version_info.minor}.{sys.version_info.micro}",
            "webhook_url": get_webhook_url(),
            "environment": {
                "webhook_url_env": os.getenv("WEBHOOK_URL", "NOT_SET"),
                "telegram_bot_token_env": "SET" if os.getenv("TELEGRAM_BOT_TOKEN") else "NOT_SET",
            },
            "timestamp": datetime.now().isoformat()
        })
    }