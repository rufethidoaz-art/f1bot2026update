# Telegram Bot Configuration Guide

## Setting up your F1 Telegram Bot

### 1. Get Your Bot Token
1. Open Telegram and search for **@BotFather**
2. Send `/newbot` to create a new bot
3. Follow the instructions to name your bot
4. BotFather will provide you with a **bot token** (looks like: `123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890`)

### 2. Configure Webhook
To set up the webhook for your bot, use one of these methods:

#### Method 1: Using BotFather (Recommended)
1. In Telegram, message **@BotFather**
2. Send the command: `/setwebhook`
3. When prompted, enter your webhook URL:
   - **For local testing with ngrok:** `https://your-ngrok-url.ngrok-free.dev/webhook`
   - **For Leapcell deployment:** `https://your-leapcell-app-url/webhook`

#### Method 2: Using curl command
```bash
curl -X POST https://api.telegram.org/botYOUR_BOT_TOKEN8460437666:AAHq-XBtLs40zv7YDiA8RH2yUkAEKqNmhmE/setWebhook -d "url=https://kam-schizocarpous-sondra.ngrok-free.dev/webhook"
```

Replace `YOUR_BOT_TOKEN` with your actual bot token.

### 3. Update Environment Variables
1. Open the `.env` file in your project directory
2. Replace `your_bot_token_here` with your actual bot token:
   ```
   TELEGRAM_BOT_TOKEN=123456789:ABCdefGHIjklMNOpqrsTUVwxyz1234567890
   ```

### 4. Test Your Bot
1. Start your local server: `python app.py`
2. Make sure ngrok is running and forwarding to localhost:8080
3. In Telegram, search for your bot by name and start a chat
4. Send commands like:
   - `/start` - Start the bot
   - `/menu` - Show main menu
   - `/standings` - Get driver standings
   - `/live` - Get live timing
   - `/nextrace` - Get next race information

### 5. Common Telegram Bot Settings

#### Set Bot Description
```
/setdescription
```

#### Set Bot Commands
```
/setcommands
```
Available commands:
```
start - Start the bot
menu - Show main menu
standings - Get driver standings
constructors - Get constructor standings
lastrace - Get last race results
nextrace - Get next race information
live - Get live timing
streams - Show available streams
addstream - Add a new stream
removestream - Remove a stream
playstream - Play a stream
streamhelp - Get stream help
```

#### Set Bot Profile Picture
```
/setuserpic
```

#### Set Bot Privacy Mode
For group functionality, you may need to disable privacy mode:
```
/setprivacy
```
Choose your bot and select "Disable"

### 6. Troubleshooting

#### Bot not responding?
- Check that your webhook is correctly set
- Verify your bot token in `.env` file
- Ensure your server is running and accessible
- Check ngrok is forwarding correctly

#### Webhook not working?
- Test your webhook URL in browser
- Check ngrok status at http://127.0.0.1:4040
- Verify your server logs for errors

#### Commands not working?
- Ensure bot commands are set in BotFather
- Check that your bot is in the correct privacy mode
- Verify your server is processing webhook requests

### 7. For Leapcell Deployment

When you deploy to Leapcell:
1. Set the webhook to your Leapcell URL: `https://your-leapcell-app-url/webhook`
2. Add your bot token as an environment variable in Leapcell dashboard
3. Test the deployed bot with the same commands

### 8. Security Notes
- Never share your bot token publicly
- Use HTTPS for webhook URLs in production
- Consider using secret tokens for webhook verification