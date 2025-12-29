"""
F1 Telegram Bot - Vercel Version with Live Timing
Main Flask application for Vercel deployment with enhanced logging
"""

import os
import sys
import logging
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

# Configure enhanced logging for Vercel
logging.basicConfig(
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
    level=logging.INFO,
    handlers=[
        logging.StreamHandler(sys.stdout),
        logging.FileHandler("bot.log", mode="a"),
    ],
)
logger = logging.getLogger(__name__)

# Create Flask app
app = Flask(__name__)

# Global reference for bot application
BOT_APP = None


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
    """Health check endpoint for Vercel"""
    logger.info("Health check requested")
    return {
        "status": "F1 Telegram Bot is running!",
        "version": "1.0.0",
        "timestamp": "2025-12-29T08:26:00Z",
        "deployment": "Vercel",
        "live_timing": "enabled",
        "logging": "enhanced",
    }


@app.route("/health")
def health_check():
    """Health check endpoint"""
    logger.info("Health check endpoint called")
    return {
        "status": "healthy",
        "service": "F1 Telegram Bot",
        "deployment": "Vercel",
        "live_timing": "enabled",
    }


@app.route("/webhook", methods=["POST"])
async def webhook():
    """Telegram webhook endpoint with enhanced logging"""
    global BOT_APP

    logger.info(f"Webhook called with method: {request.method}")
    logger.info(f"Request headers: {dict(request.headers)}")

    if BOT_APP is None:
        logger.info("Bot application not initialized, setting up...")
        BOT_APP = setup_bot()
        if BOT_APP is None:
            logger.error("Failed to setup bot application")
            return jsonify({"error": "Bot not configured"}), 500
        logger.info("Bot application initialized successfully")

    try:
        logger.info("Processing webhook request...")
        update = Update.de_json(request.get_json(force=True), BOT_APP.bot)
        logger.info(
            f"Received update from user: {update.effective_user.id if update.effective_user else 'unknown'}"
        )
        logger.info(f"Update type: {type(update)}")

        await BOT_APP.process_update(update)
        logger.info("Webhook processed successfully")
        return jsonify({"status": "ok", "message": "Update processed"}), 200
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
    BOT_APP = setup_bot()
    if BOT_APP:
        logger.info("Bot started successfully in local mode")
        app.run(host="0.0.0.0", port=int(os.environ.get("PORT", 8080)))
    else:
        logger.error("Failed to start bot")
        sys.exit(1)
