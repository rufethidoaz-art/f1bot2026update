"""
Vercel Serverless Function for Telegram Webhook
F1 Telegram Bot - Optimized for Vercel deployment
"""

import os
import sys
import asyncio
import logging
from datetime import datetime
from http import HTTPStatus

# Add parent directory to path to import bot modules
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from telegram import Update, Bot
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Import bot handlers from existing modules
from f1_bot_live import (
    start,
    show_menu,
    button_handler,
    live_cmd,
    get_current_standings,
    get_constructor_standings,
    get_last_session_results,
    get_next_race,
)

# Configure logging
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

# Global bot application instance
BOT_APP = None
BOT_INITIALIZED = False

# Cache for processed updates to prevent duplicates
PROCESSED_UPDATES = set()
MAX_PROCESSED_UPDATES = 1000

def get_bot_token():
    """Get bot token from environment"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if not token:
        logger.error("TELEGRAM_BOT_TOKEN environment variable is not set")
        return None
    return token

def get_webhook_url():
    """Get webhook URL from environment"""
    return os.getenv("WEBHOOK_URL", "")

def is_update_processed(update_id):
    """Check if update has already been processed"""
    return update_id in PROCESSED_UPDATES

def mark_update_processed(update_id):
    """Mark update as processed"""
    PROCESSED_UPDATES.add(update_id)
    # Keep only recent updates to prevent memory issues
    if len(PROCESSED_UPDATES) > MAX_PROCESSED_UPDATES:
        PROCESSED_UPDATES.clear()

async def setup_bot():
    """Initialize the Telegram bot application"""
    logger.info("Setting up Telegram bot application...")
    
    token = get_bot_token()
    if not token:
        return None
    
    try:
        # Create HTTPXRequest with optimized settings for serverless
        import httpx
        from telegram.request import HTTPXRequest
        
        httpx_request = HTTPXRequest(
            connection_pool_size=10,
            read_timeout=30.0,
            write_timeout=30.0,
            connect_timeout=30.0,
            pool_timeout=30.0
        )
        
        # Ensure the client is initialized
        if not hasattr(httpx_request, '_client') or httpx_request._client is None:
            httpx_request._client = httpx.AsyncClient(
                limits=httpx.Limits(max_connections=10, max_keepalive_connections=5),
                timeout=httpx.Timeout(30.0, read=30.0, write=30.0, pool=30.0),
            )
        
        application = (
            Application.builder()
            .token(token)
            .request(httpx_request)
            .concurrent_updates(True)
            .build()
        )
        
        # Initialize the application
        await application.initialize()
        
        # Add handlers
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("menu", show_menu))
        
        # Async wrapper functions for command handlers
        async def standings_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message:
                await update.message.reply_text("⏳ Yüklənir...")
                message = get_current_standings()
                await update.message.reply_text(message, parse_mode="Markdown")
        
        async def constructors_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message:
                await update.message.reply_text("⏳ Yüklənir...")
                message = get_constructor_standings()
                await update.message.reply_text(message, parse_mode="Markdown")
        
        async def lastrace_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message:
                await update.message.reply_text("⏳ Yüklənir...")
                message = get_last_session_results()
                await update.message.reply_text(message, parse_mode="Markdown")
        
        async def nextrace_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
            if update.message:
                await update.message.reply_text("⏳ Yüklənir...")
                message = get_next_race()
                await update.message.reply_text(message, parse_mode="Markdown")
        
        application.add_handler(CommandHandler("standings", standings_handler))
        application.add_handler(CommandHandler("constructors", constructors_handler))
        application.add_handler(CommandHandler("lastrace", lastrace_handler))
        application.add_handler(CommandHandler("nextrace", nextrace_handler))
        application.add_handler(CommandHandler("live", live_cmd))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info("✅ Bot setup successful")
        return application
        
    except Exception as e:
        logger.error(f"❌ Bot setup failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

async def initialize_bot():
    """Initialize bot application"""
    global BOT_APP, BOT_INITIALIZED
    
    if BOT_INITIALIZED:
        logger.info("✅ Bot already initialized")
        return True
    
    try:
        bot_app = await setup_bot()
        if not bot_app:
            logger.error("❌ Bot setup failed")
            return False
        
        BOT_APP = bot_app
        BOT_INITIALIZED = True
        logger.info("✅ Bot application initialized successfully")
        
        # Set webhook if URL is provided
        webhook_url = get_webhook_url()
        if webhook_url:
            try:
                bot = bot_app.bot
                result = await bot.set_webhook(url=webhook_url)
                if result:
                    logger.info(f"✅ Webhook set to: {webhook_url}")
                else:
                    logger.warning("⚠️ Webhook set returned False")
            except Exception as e:
                logger.warning(f"⚠️ Could not set webhook: {e}")
        
        return True
        
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

async def process_update_isolated(bot_app, update, update_id):
    """Process update in isolated context"""
    try:
        if bot_app is None:
            logger.error(f"❌ Bot app is None for update {update_id}")
            return
        
        await bot_app.process_update(update)
        logger.info(f"✅ Update {update_id} processed successfully")
        
    except Exception as e:
        logger.error(f"❌ Error processing update {update_id}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

async def webhook_handler(event):
    """Main webhook handler for Vercel"""
    global BOT_APP
    
    try:
        # Parse the incoming request
        if event.get('httpMethod') != 'POST':
            return {
                'statusCode': HTTPStatus.METHOD_NOT_ALLOWED,
                'body': 'Method Not Allowed'
            }
        
        # Get JSON body
        body = event.get('body')
        if not body:
            return {
                'statusCode': HTTPStatus.BAD_REQUEST,
                'body': 'Bad Request: Empty body'
            }
        
        import json
        try:
            json_data = json.loads(body)
        except json.JSONDecodeError:
            return {
                'statusCode': HTTPStatus.BAD_REQUEST,
                'body': 'Bad Request: Invalid JSON'
            }
        
        update_id = json_data.get('update_id', 'unknown')
        logger.info(f"📥 Update {update_id} received")
        
        # Check for duplicates
        if is_update_processed(update_id):
            logger.info(f"⚠️ Duplicate update {update_id} detected, skipping")
            return {
                'statusCode': HTTPStatus.OK,
                'body': '{"status": "ok", "message": "duplicate"}'
            }
        
        mark_update_processed(update_id)
        
        # Initialize bot if needed
        if BOT_APP is None:
            logger.info("Initializing bot application...")
            success = await initialize_bot()
            if not success:
                logger.error("❌ Failed to initialize bot")
                return {
                    'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
                    'body': '{"status": "error", "message": "Bot initialization failed"}'
                }
        
        # Process the update
        bot_app = BOT_APP
        if bot_app is None or not hasattr(bot_app, "bot") or bot_app.bot is None:
            logger.error("Bot app or bot is None")
            return {
                'statusCode': HTTPStatus.OK,
                'body': '{"status": "ok", "message": "bot_not_ready"}'
            }
        
        bot = bot_app.bot
        update = Update.de_json(json_data, bot)
        if update is None:
            logger.warning("Failed to create update object")
            return {
                'statusCode': HTTPStatus.OK,
                'body': '{"status": "ok", "message": "invalid_update"}'
            }
        
        # Process update
        await process_update_isolated(bot_app, update, update_id)
        
        return {
            'statusCode': HTTPStatus.OK,
            'body': '{"status": "ok"}'
        }
        
    except Exception as e:
        logger.error(f"❌ Error in webhook handler: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        
        return {
            'statusCode': HTTPStatus.INTERNAL_SERVER_ERROR,
            'body': '{"status": "error", "message": "Internal server error"}'
        }

# Vercel expects the handler to be exported as 'default'
async def default(event, context):
    """Vercel serverless function entry point"""
    return await webhook_handler(event)

# For local testing
if __name__ == "__main__":
    print("This is a Vercel serverless function. Use 'vercel dev' to test locally.")