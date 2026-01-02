from flask import Flask, request
import threading
import requests
import os  # to access environment variables

app = Flask(__name__)

# Get Telegram bot token from environment variable
telegram_token = os.environ.get("TELEGRAM_BOT_TOKEN")
if not telegram_token:
    raise ValueError("TELEGRAM_BOT_TOKEN is not set in environment variables")

# --------------------------
# POST endpoint for Telegram
# --------------------------
@app.route("/", methods=["POST"])
def webhook():
    update = request.get_json(silent=True)
    if update:
        threading.Thread(target=process_update, args=(update,)).start()
    return "OK", 200

# --------------------------
# GET endpoint for status
# --------------------------
@app.route("/", methods=["GET"])
def home():
    return {
        "deployment": "Leapcell",
        "status": "F1 Telegram Bot is running!",
        "version": "1.2.0",
        "webhook_url": "https://f1bot2026update-rufethidoaz6750-xgug3pqz.leapcell.dev/"
    }

# --------------------------
# Process Telegram update
# --------------------------
def process_update(update):
    try:
        message = update.get("message")
        if not message:
            return

        chat_id = message["chat"]["id"]
        text = message.get("text", "")

        answer = generate_response(text)

        requests.post(
            f"https://api.telegram.org/bot{telegram_token}/sendMessage",
            json={"chat_id": chat_id, "text": answer}
        )
    except Exception as e:
        print("Error processing update:", e)

# --------------------------
# Example response generator
# --------------------------
def generate_response(text):
    return f"You said: {text}"

# --------------------------
# Run app
# --------------------------
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000)