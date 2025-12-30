"""
F1 Telegram Bot - Leapcell Version with Live Timing
Main Flask application for Leapcell deployment with enhanced logging
FINAL WORKING VERSION with thread-safe queue
"""

import os
import sys
import logging
import asyncio
import threading
import queue
from flask import Flask, request, jsonify
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackQueryHandler, ContextTypes

# Import bot functionality
from f1_bot_live import (
    start,
    show_menu,
    button_handler,
    standings_cmd,
    constructors_cmd,
    lastrace_cmd,
    nextrace_cmd,
    live_cmd,
    streams_cmd,
    addstream_cmd,
    removestream_cmd,
    streamhelp_cmd,
    playstream_cmd,
)

# Configure enhanced logging for Leapcell
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
    ],
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global reference for bot application
BOT_APP = None

# Thread-safe queue for webhook updates
update_queue = queue.Queue()


def bot_worker():
    """Background worker to process bot updates"""
    global BOT_APP, update_queue

    logger.info("Bot worker thread starting...")

    # Create new event loop for this thread
    loop = asyncio.new_event_loop()
    asyncio.set_event_loop(loop)

    try:
        logger.info("Bot worker event loop created")

        # Initialize bot if not already done
        if BOT_APP is None:
            logger.info("Bot worker initializing bot application...")
            BOT_APP = setup_bot()
            if BOT_APP:
                logger.info("Bot worker setting up bot handlers...")
                loop.run_until_complete(BOT_APP.initialize())
                logger.info("Bot worker initialized successfully")
            else:
                logger.error("Failed to initialize bot in worker")
                return
        else:
            logger.info("Bot worker using existing bot application")

        # Process updates from queue
        logger.info("Bot worker starting update processing loop...")
        while True:
            try:
                logger.info("Bot worker waiting for updates...")
                # Use regular queue.get() instead of asyncio
                update = update_queue.get(timeout=1)
                if update is None:  # Poison pill to stop worker
                    logger.info("Bot worker received stop signal")
                    break

                logger.info(f"Bot worker processing update: {update.update_id}")
                loop.run_until_complete(BOT_APP.process_update(update))
                logger.info(
                    f"Bot worker processed update {update.update_id} successfully"
                )

            except queue.Empty:
                # Timeout is normal, just continue
                continue
            except Exception as e:
                logger.error(f"Error in bot worker: {e}")
                import traceback

                logger.error(f"Worker error traceback: {traceback.format_exc()}")

    except Exception as e:
        logger.error(f"Bot worker failed with exception: {e}")
        import traceback

        logger.error(f"Worker startup error traceback: {traceback.format_exc()}")
    finally:
        logger.info("Bot worker shutting down...")
        loop.close()
        logger.info("Bot worker event loop closed")


def setup_bot():
    """Setup and return the Telegram bot application"""
    try:
        from dotenv import load_dotenv

        load_dotenv(override=False)
    except ImportError:
        # Fallback: manually read .env file if python-dotenv is not installed
        if not os.getenv("TELEGRAM_BOT_TOKEN") and os.path.exists(".env"):
            try:
                with open(".env", "r", encoding="utf-8") as f:
                    for line in f:
                        line = line.strip()
                        if line and not line.startswith("#") and "=" in line:
                            key, value = line.split("=", 1)
                            key = key.strip()
                            value = value.strip().strip('"').strip("'")
                            if not os.getenv(key):
                                os.environ[key] = value
            except Exception as e:
                logger.error(f"Error reading .env file: {e}")
                pass

    # Get bot token from environment variable
    BOT_TOKEN = os.getenv("TELEGRAM_BOT_TOKEN")

    if not BOT_TOKEN:
        logger.error("TELEGRAM_BOT_TOKEN is not set!")
        logger.error("Get your token from @BotFather: https://t.me/BotFather")
        return None

    logger.info("Setting up Telegram bot application...")

    # Create application with proper configuration for v20.7
    application = Application.builder().token(BOT_TOKEN).build()

    # Add handlers
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("menu", show_menu))
    application.add_handler(CommandHandler("standings", standings_cmd))
    application.add_handler(CommandHandler("constructors", constructors_cmd))
    application.add_handler(CommandHandler("lastrace", lastrace_cmd))
    application.add_handler(CommandHandler("nextrace", nextrace_cmd))
    application.add_handler(CommandHandler("live", live_cmd))
    application.add_handler(CommandHandler("streams", streams_cmd))
    application.add_handler(CommandHandler("addstream", addstream_cmd))
    application.add_handler(CommandHandler("removestream", removestream_cmd))
    application.add_handler(CommandHandler("playstream", playstream_cmd))
    application.add_handler(CommandHandler("streamhelp", streamhelp_cmd))
    application.add_handler(CallbackQueryHandler(button_handler))

    logger.info("Bot handlers configured successfully")
    return application


@app.route("/")
def home():
    """Health check endpoint for Leapcell"""
    logger.info("Health check requested")
    return {
        "status": "F1 Telegram Bot is running!",
        "version": "1.0.2",
        "timestamp": "2025-12-29T13:16:00Z",
        "deployment": "Leapcell",
        "live_timing": "enabled",
        "logging": "enhanced",
        "async_fix": "worker_thread_queue",
    }


@app.route("/health")
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "service": "F1 Telegram Bot",
        "deployment": "Leapcell",
        "live_timing": "enabled",
    }


@app.route("/test-webhook", methods=["GET", "POST"])
def test_webhook():
    """Test webhook endpoint for debugging"""
    logger.info(f"Test webhook called with method: {request.method}")
    
    if request.method == "GET":
        return jsonify({
            "status": "test_webhook_working",
            "message": "Webhook endpoint is accessible",
            "bot_token_set": bool(os.getenv("TELEGRAM_BOT_TOKEN")),
            "deployment": "Leapcell"
        })
    
    elif request.method == "POST":
        try:
            json_data = request.get_json(force=True)
            logger.info(f"Test webhook received data: {json_data}")
            return jsonify({
                "status": "test_webhook_received",
                "message": "Webhook test successful",
                "received_data": json_data
            })
        except Exception as e:
            logger.error(f"Error in test webhook: {e}")
            return jsonify({"status": "error", "message": str(e)}), 400
    
    return jsonify({"status": "unknown_method", "message": "Method not supported"}), 405


@app.route("/webhook", methods=["POST"])
def webhook():
    """Telegram webhook endpoint with enhanced logging"""
    global BOT_APP, update_queue

    logger.info(f"Webhook called with method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")

    try:
        logger.info("Processing webhook request...")
        # Parse JSON data safely
        json_data = request.get_json(force=True)
        if not json_data:
            return jsonify({"error": "Invalid JSON data"}), 400

        logger.info(f"Parsed JSON data: {json_data}")
        logger.info(f"JSON data type: {type(json_data)}")

        # Initialize bot if not already done
        if BOT_APP is None:
            logger.info("Bot application not initialized, initializing now...")
            BOT_APP = setup_bot()
            if BOT_APP is None:
                logger.error("Failed to initialize bot application")
                return jsonify({"error": "Bot initialization failed"}), 500
            logger.info("Bot application initialized successfully")

        # Create update object
        update = Update.de_json(json_data, BOT_APP.bot)
        user_id = "unknown"
        if update and hasattr(update, 'effective_user') and update.effective_user:
            user_id = str(update.effective_user.id)
        logger.info(f"Received update from user: {user_id}")
        logger.info(f"Update type: {type(update)}")

        # Process the update directly for LEAPCELL (since worker thread may not work)
        try:
            logger.info("Processing update directly...")
            # Initialize bot if not already done
            if not BOT_APP:
                logger.error("Bot application still not initialized")
                return jsonify({"error": "Bot not initialized"}), 500
            
            # Run the update processing in the event loop
            import asyncio
            loop = asyncio.new_event_loop()
            asyncio.set_event_loop(loop)
            try:
                # Initialize the bot application first
                logger.info("Initializing bot application...")
                loop.run_until_complete(BOT_APP.initialize())
                logger.info("Bot application initialized, processing update...")
                
                # Process the update directly
                loop.run_until_complete(BOT_APP.process_update(update))
                update_id = getattr(update, 'update_id', 'unknown') if update else 'unknown'
                logger.info(f"Successfully processed update {update_id}")
                return jsonify({"status": "ok", "message": "Update processed successfully"}), 200
            except Exception as e:
                logger.error(f"Error processing update: {e}")
                return jsonify({"status": "error", "message": str(e)}), 500
            finally:
                loop.close()
                
        except Exception as e:
            logger.error(f"Error in direct update processing: {e}")
            return jsonify({"status": "error", "message": str(e)}), 500
    except Exception as e:
        logger.error(f"Error processing webhook: {e}")
        logger.error(f"Request data: {request.get_data()}")
        return jsonify({"error": str(e)}), 500


@app.route("/logs")
def get_logs():
    """Endpoint to retrieve bot logs (for debugging)"""
    try:
        if os.path.exists("bot.log"):
            with open("bot.log", "r", encoding="utf-8") as f:
                logs = f.read()
            return jsonify({"logs": logs[-2000:]}), 200  # Return last 2000 chars
        else:
            return jsonify({"logs": "No logs available"}), 200
    except Exception as e:
        logger.error(f"Error reading logs: {e}")
        return jsonify({"error": str(e)}), 500


if __name__ == "__main__":
    # Local development mode
    logger.info("Starting F1 Bot in local mode...")

    # Start bot worker thread (non-daemon so it stays alive)
    worker_thread = threading.Thread(target=bot_worker, daemon=False)
    worker_thread.start()
    logger.info(f"Bot worker thread started (Thread ID: {worker_thread.ident})")

    # Initialize bot in main thread for webhook creation
    BOT_APP = setup_bot()
    if BOT_APP:
        logger.info("Bot started successfully in local mode")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    else:
        logger.error("Failed to start bot")
        sys.exit(1)
