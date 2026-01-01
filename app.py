"""
F1 Telegram Bot - FIXED VERSION
Solves the double-call issue with proper webhook handling
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

# Initialize bot on module import (works with Gunicorn)
async def initialize_bot_on_startup():
    """Initialize bot when module is imported"""
    global BOT_APP
    logger.info("🚀 Starting bot initialization on module import...")
    try:
        success = await initialize_bot_app()
        if success:
            logger.info("✅ Bot initialized successfully on startup!")
        else:
            logger.warning("⚠️ Bot initialization failed on startup")
    except Exception as e:
        logger.error(f"❌ Startup initialization error: {e}")

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

# Run initialization in main process (not in Gunicorn workers)
if __name__ == "__main__":
    asyncio.run(initialize_bot_on_startup())

async def setup_bot():
    logger.info("=== BOT INITIALIZATION START ===")
    BOT_TOKEN = get_bot_token()
    logger.info(f"Bot token retrieved: {'YES' if BOT_TOKEN else 'NO'}")
    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
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
    global BOT_APP
    try:
        bot_app = await setup_bot()
        if bot_app:
            await bot_app.initialize()
            BOT_APP = bot_app
            logger.info("✅ Bot application initialized successfully")
            return True
    except Exception as e:
        logger.error(f"❌ Failed to initialize bot: {e}")
        BOT_APP = None
    return False

update_queue = Queue()

async def process_update_async(bot_app, update, update_id):
    """Process update asynchronously"""
    try:
        await bot_app.process_update(update)
        logger.info(f"✅ Update {update_id} processed successfully")
    except Exception as e:
        logger.error(f"❌ Error processing update {update_id}: {e}")

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

    # Start the queue watcher
    watcher_thread = Thread(target=queue_watcher, daemon=True)
    watcher_thread.start()
    loop.run_forever()


@app.route("/")
def home():
    return {
        "status": "F1 Telegram Bot is running!",
        "version": "1.1.0",
        "fix": "double_call_issue_solved",
        "deployment": "Leapcell",
    }

@app.route("/health")
def health_check():
    return {
        "status": "healthy",
        "initialized": BOT_APP is not None,
    }

@app.route("/webhook", methods=["POST"])
def webhook():
    global BOT_APP
    json_data = request.get_json(force=True, silent=True)
    if not json_data:
        logger.warning("Invalid JSON received")
        return jsonify({"status": "ok"}), 200
    update_id = json_data.get("update_id", "unknown")
    logger.info(f"📥 Update {update_id} received")
    try:
        if BOT_APP is None:
            logger.info("Bot not initialized, setting up...")
            success = asyncio.run(initialize_bot_app())
            if not success:
                return jsonify({"status": "ok", "message": "Bot init failed"}), 200
        bot_app = BOT_APP
        if bot_app is None or not hasattr(bot_app, "bot") or bot_app.bot is None:
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
    return jsonify({"status": "ok"}), 200

@app.route("/debug")
def debug():
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
        "version": "1.1.0",
        "imports": import_status,
        "python_version": f"{__import__('sys').version_info.major}.{__import__('sys').version_info.minor}",
    })

if __name__ == "__main__":
    try:
        success = asyncio.run(initialize_bot_app())
        if success:
            logger.info("✅ Bot initialized on startup - commands will work on first try!")
        else:
            logger.warning("⚠️ Bot initialization failed - will try on first request")
    except Exception as e:
        logger.error(f"Startup error: {e}")
    # Start background processing thread
    background_thread = Thread(target=process_updates_background, daemon=True)
    background_thread.start()
    logger.info("🌐 Flask server starting...")
    app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)), debug=False, threaded=True)
