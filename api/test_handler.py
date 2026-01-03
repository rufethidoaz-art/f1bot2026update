"""
Test handler to understand Vercel's expected format
"""

def handler(event, context):
    """Simple test handler"""
    return {
        'statusCode': 200,
        'headers': {'Content-Type': 'application/json'},
        'body': '{"status": "test", "message": "Hello from Vercel"}'
    }

# Also try with 'app' for Flask compatibility
app = handler