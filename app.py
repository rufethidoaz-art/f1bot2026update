"""
F1 Telegram Bot - FINAL FIXED VERSION
Solves webhook domain issues and initialization problems
"""

import os
import sys
import logging
import asyncio
from queue import Queue
from threading import Thread
from flask import Flask, request, jsonify
from telegram import Update, Bot, Message
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

from f1_bot_live import (
    start,
    show_menu,
    button_handler,
    standings_cmd,
    constructors_cmd,
    lastrace_cmd,
    nextrace_cmd,
    live_cmd,
)

logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[logging.StreamHandler(sys.stdout)],
)
logger = logging.getLogger(__name__)

app = Flask(__name__)

BOT_APP = None
update_queue = Queue()
WEBHOOK_SET = False  # CRITICAL: Prevents repeated webhook attempts

# Get webhook URL from environment variable
def get_webhook_url():
    """Get webhook URL from environment or use the async domain"""
    return os.getenv("WEBHOOK_URL", "https://f1bot2026update-rufethidoaz6750-q9iv49mppvjya4t35r.leapcell.dev/webhook")

def get_bot_token():
    """Get bot token from environment or .env file"""
    token = os.getenv("TELEGRAM_BOT_TOKEN")
    if token:
        return token
    try:
        from dotenv import load_dotenv
        load_dotenv(override=False)
        token = os.getenv("TELEGRAM_BOT_TOKEN")
        if token:
            return token
    except ImportError:
        pass
    if os.path.exists(".env"):
        try:
            with open(".env", "r", encoding="utf-8") as f:
                for line in f:
                    line = line.strip()
                    if line and not line.startswith("#") and "=" in line:
                        key, value = line.split("=", 1)
                        key = key.strip()
                        value = value.strip().strip('"').strip("'")
                        if key == "TELEGRAM_BOT_TOKEN" and not os.getenv(key):
                            return value
        except Exception as e:
            logger.error(f"Error reading .env file: {e}")
    return None

def process_updates_background():
    """Background thread to process updates asynchronously"""
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    async def process_item(item):
        if item is None:
            loop.stop()
            return
        bot_app, update, update_id = item
        await process_update_async(bot_app, update, update_id)

    def queue_watcher():
        while True:
            item = update_queue.get()
            asyncio.run_coroutine_threadsafe(process_item(item), loop)

    watcher_thread = Thread(target=queue_watcher, daemon=True)
    watcher_thread.start()
    loop.run_forever()

async def setup_bot():
    """Initialize the Telegram bot application"""
    logger.info("=== BOT INITIALIZATION START ===")
    BOT_TOKEN = get_bot_token()
    logger.info(f"Bot token retrieved: {'YES' if BOT_TOKEN else 'NO'}")
    if not BOT_TOKEN:
        logger.error("❌ TELEGRAM_BOT_TOKEN is not set!")
        logger.error("Please set your Telegram bot token in the .env file or environment variables")
        logger.error("Get your bot token from @BotFather in Telegram")
        return None
    
    logger.info("Setting up Telegram bot application...")
    try:
        logger.info("Creating Application builder...")
        application = (
            Application.builder()
            .token(BOT_TOKEN)
            .concurrent_updates(True)
            .build()
        )
        logger.info("Application created, adding handlers...")
        application.add_handler(CommandHandler("start", start))
        application.add_handler(CommandHandler("menu", show_menu))
        application.add_handler(CommandHandler("standings", standings_cmd))
        application.add_handler(CommandHandler("constructors", constructors_cmd))
        application.add_handler(CommandHandler("lastrace", lastrace_cmd))
        application.add_handler(CommandHandler("nextrace", nextrace_cmd))
        application.add_handler(CommandHandler("live", live_cmd))
        application.add_handler(CallbackQueryHandler(button_handler))
        
        logger.info("✅ Bot setup successful")
        logger.info("=== BOT INITIALIZATION COMPLETE ===")
        return application
    except Exception as e:
        logger.error(f"❌ Bot setup failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return None

async def initialize_bot_app():
    """Initialize bot application and set webhook with flood control handling"""
    global BOT_APP, WEBHOOK_SET
    
    # CRITICAL: Skip initialization if already done
    if WEBHOOK_SET:
        logger.info("✅ Bot already initialized, skipping webhook setup")
        return True
    
    try:
        # Setup bot application
        bot_app = await setup_bot()
        if not bot_app:
            logger.error("❌ Bot setup failed - no bot application")
            return False
            
        await bot_app.initialize()
        BOT_APP = bot_app
        logger.info("✅ Bot application initialized successfully")
        
        # CRITICAL: Check if webhook is already set BEFORE trying to set it
        webhook_url = get_webhook_url()
        bot = bot_app.bot
        
        try:
            # Check current webhook status
            webhook_info = await bot.get_webhook_info()
            current_url = webhook_info.url
            
            if current_url and current_url == webhook_url:
                logger.info(f"✅ Webhook already set to correct URL: {webhook_url}")
                WEBHOOK_SET = True
                return True
            elif current_url:
                logger.info(f"🔄 Webhook exists but wrong URL. Current: {current_url}, Needed: {webhook_url}")
            else:
                logger.info("🆕 No webhook set, will set new one")
                
        except Exception as e:
            if "webhook is not set" in str(e).lower():
                logger.info("🆕 No existing webhook found")
            else:
                logger.warning(f"⚠️ Could not check webhook status: {e}")
         
        # CRITICAL: Only set webhook if not already set
        try:
            logger.info(f"🔧 Setting webhook to: {webhook_url}")
            result = await bot.set_webhook(url=webhook_url)
             
            if result:
                WEBHOOK_SET = True
                logger.info(f"✅ Webhook successfully set to: {webhook_url}")
                return True
            else:
                logger.error("❌ Webhook set returned False")
                return False
                 
        except Exception as e:
            # CRITICAL: Handle flood control gracefully
            error_str = str(e)
            if "Retry after" in error_str or "Flood control" in error_str:
                logger.warning(f"⚠️ Telegram flood control activated! {e}")
                logger.warning("⏳ Waiting before retry...")
                await asyncio.sleep(10)  # Wait 10 seconds for flood control
                return await initialize_bot_app()  # Retry after delay
            else:
                logger.error(f"❌ Failed to set webhook: {e}")
                import traceback
                logger.error(f"Full traceback: {traceback.format_exc()}")
                return False
            
    except Exception as e:
        logger.error(f"❌ Bot initialization failed: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

async def process_update_async(bot_app, update, update_id):
    """Process update asynchronously"""
    try:
        await bot_app.process_update(update)
        logger.info(f"✅ Update {update_id} processed successfully")
    except Exception as e:
        logger.error(f"❌ Error processing update {update_id}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

@app.route("/")
def home():
    return {
        "status": "F1 Telegram Bot is running!",
        "version": "1.2.0",
        "fix": "webhook_domain_issue_fixed",
        "deployment": "Leapcell",
        "webhook_url": get_webhook_url(),
    }

@app.route("/health")
def health_check():
    return {
        "status": "healthy",
        "initialized": BOT_APP is not None,
        "webhook_url": get_webhook_url(),
    }

@app.route("/webhook", methods=["POST"])
def webhook():
    """Handle incoming webhook updates from Telegram"""
    global BOT_APP
    json_data = request.get_json(force=True, silent=True)
    if not json_data:
        logger.warning("Invalid JSON received")
        return jsonify({"status": "ok"}), 200
    
    update_id = json_data.get("update_id", "unknown")
    logger.info(f"📥 Update {update_id} received")
    logger.info(f"Update data keys: {list(json_data.keys())}")
    
    try:
        if BOT_APP is None:
            logger.info("Bot not initialized, setting up...")
            success = asyncio.run(initialize_bot_app())
            if not success:
                logger.error("❌ Failed to initialize bot")
                return jsonify({"status": "error", "message": "Bot initialization failed - check logs for details"}), 500
        
        bot_app = BOT_APP
        if bot_app is None or not hasattr(bot_app, "bot") or bot_app.bot is None:
            logger.error("Bot app or bot is None")
            return jsonify({"status": "ok"}), 200
        
        bot = bot_app.bot
        update = Update.de_json(json_data, bot)
        if update is None:
            logger.warning("Failed to create update object")
            return jsonify({"status": "ok"}), 200
        
        update_queue.put((bot_app, update, update_id))
        logger.info(f"📤 Update {update_id} queued for processing")
        
    except Exception as e:
        logger.error(f"❌ Error processing update {update_id}: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
    
    return jsonify({"status": "ok"}), 200

@app.route("/debug")
def debug():
    """Debug endpoint to check bot status"""
    token = get_bot_token()
    import_status = {}
    
    try:
        from f1_bot_live import start, get_current_standings
        import_status["f1_bot_live"] = "OK"
    except Exception as e:
        import_status["f1_bot_live"] = f"ERROR: {e}"

    try:
        import telegram
        import_status["telegram"] = f"OK (v{telegram.__version__})"
    except Exception as e:
        import_status["telegram"] = f"ERROR: {e}"

    return jsonify({
        "bot_token_set": bool(token),
        "bot_initialized": BOT_APP is not None,
        "version": "1.2.0",
        "imports": import_status,
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
        "webhook_url": get_webhook_url(),
        "environment": {
            "webhook_url_env": os.getenv("WEBHOOK_URL", "NOT_SET"),
            "telegram_bot_token_env": "SET" if os.getenv("TELEGRAM_BOT_TOKEN") else "NOT_SET",
        }
    })

@app.route("/webhook-info")
def webhook_info():
    """Endpoint to check webhook status"""
    webhook_url = get_webhook_url()
    return jsonify({
        "webhook_url": webhook_url,
        "bot_initialized": BOT_APP is not None,
    })

@app.route("/set-webhook", methods=["POST"])
def manual_set_webhook():
    """Endpoint to manually set the webhook"""
    global BOT_APP
    if BOT_APP is None:
        return jsonify({"status": "error", "message": "Bot not initialized"}), 500
    
    try:
        webhook_url = get_webhook_url()
        logger.info(f"Manually setting webhook to: {webhook_url}")
        success = asyncio.run(set_webhook_manually(webhook_url))
        if success:
            logger.info("✅ Webhook set successfully")
            return jsonify({"status": "success", "webhook_url": webhook_url}), 200
        else:
            logger.warning("⚠️ Failed to set webhook")
            return jsonify({"status": "error", "message": "Failed to set webhook"}), 500
    except Exception as e:
        logger.error(f"❌ Failed to set webhook manually: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return jsonify({"status": "error", "message": str(e)}), 500

async def set_webhook_manually(webhook_url):
    """Manually set webhook URL"""
    global BOT_APP
    if BOT_APP is None:
        logger.warning("Bot not initialized, cannot set webhook")
        return False
    
    try:
        bot = BOT_APP.bot
        logger.info(f"Setting webhook to: {webhook_url}")
        result = await bot.set_webhook(url=webhook_url)
        if result:
            logger.info(f"✅ Webhook set to: {webhook_url}")
            # Verify webhook is set
            webhook_info = await bot.get_webhook_info()
            logger.info(f"Webhook info: {webhook_info}")
        else:
            logger.warning("⚠️ Webhook set returned False")
        return True
    except Exception as e:
        logger.error(f"❌ Failed to set webhook: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
        return False

def main():
    """Main initialization function"""
    logger.info("🚀 Starting F1 Telegram Bot initialization...")
    
    # Initialize bot on startup
    try:
        success = asyncio.run(initialize_bot_app())
        if success:
            logger.info("✅ Bot initialized successfully on startup!")
        else:
            logger.warning("⚠️ Bot initialization failed on startup - will try on first request")
    except Exception as e:
        logger.error(f"❌ Startup initialization error: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")
     
    # Start background processing thread
    try:
        background_thread = Thread(target=process_updates_background, daemon=True)
        background_thread.start()
        logger.info("📋 Background processing thread started")
    except Exception as e:
        logger.error(f"❌ Failed to start background thread: {e}")
        import traceback
        logger.error(f"Full traceback: {traceback.format_exc()}")

# Initialize bot when Flask app starts (for Gunicorn compatibility)
def init_app():
    with app.app_context():
        main()

# Call init_app when this module is imported
init_app()

if __name__ == "__main__":
    logger.info("🌐 Flask server starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=False, threaded=True)
