# F1 Telegram Bot - Vercel Serverless Edition 🚀

A serverless F1 Telegram bot optimized for Vercel deployment with live timing support, race schedules, and driver standings.

## ✨ Features

- **Serverless Architecture**: Runs on Vercel's serverless functions
- **Live Timing**: Real-time F1 session data via OpenF1 API
- **Race Information**: Schedules, results, and weather forecasts
- **Driver & Constructor Standings**: Current championship positions
- **Playwright Support**: Web scraping for enhanced live timing
- **Automatic Webhook Management**: Self-configuring Telegram webhooks
- **Health Monitoring**: Built-in health checks and debugging

## 🚀 Quick Deploy

### 1-Click Deploy
[![Deploy with Vercel](https://vercel.com/button)](https://vercel.com/new/clone?repository-url=https://github.com/your-username/f1-bot-vercel&env=TELEGRAM_BOT_TOKEN,WEBHOOK_URL&project-name=f1-telegram-bot)

### Manual Deploy
```bash
# Clone your repository
git clone https://github.com/your-username/f1-bot-vercel
cd f1-bot-vercel

# Deploy to Vercel
vercel
```

## ⚙️ Environment Variables

Set these in Vercel dashboard (Project Settings → Environment Variables):

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token from BotFather | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `WEBHOOK_URL` | Your Vercel webhook URL (set after deployment) | `https://your-project.vercel.app/webhook` |

**Important Notes:**
- Enter the actual values, not `@variable_name` syntax
- `WEBHOOK_URL` can be set after your first deployment
- Keep `TELEGRAM_BOT_TOKEN` secret and never commit it to git

## 📁 Project Structure

```
├── api/
│   ├── webhook.py          # Main webhook handler
│   ├── health.py           # Health check
│   ├── index.py            # Info endpoint
│   ├── debug.py            # Debug info
│   ├── webhook_info.py     # Webhook status
│   └── set_webhook.py      # Webhook setup
├── f1_bot_live.py          # Bot command handlers
├── f1_playwright_scraper_fixed.py  # Live timing scraper
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel config
├── vercel-build.sh         # Build script
└── VERCEL_DEPLOYMENT_GUIDE.md  # Detailed guide
```

## 🔧 Available Commands

Once deployed, your bot supports:

- `/start` - Welcome message with menu
- `/menu` - Show command menu
- `/standings` - Driver standings
- `/constructors` - Constructor standings
- `/lastrace` - Last race results
- `/nextrace` - Next race schedule & weather
- `/live` - Live timing (when session active)

## 🌐 API Endpoints

| Endpoint | Purpose | Method |
|----------|---------|--------|
| `/webhook` | Telegram webhook handler | POST |
| `/health` | Health check | GET |
| `/debug` | Debug information | GET |
| `/webhook-info` | Webhook status | GET |
| `/set-webhook` | Set webhook manually | GET |
| `/` | Service info | GET |

## 📊 Monitoring & Debugging

### Health Check
```
https://your-project.vercel.app/health
```

### Debug Information
```
https://your-project.vercel.app/debug
```

## 🎯 Deployment Steps

1. **Import to Vercel**
   - Connect your GitHub repository
   - Framework: Other
   - Build Command: `bash vercel-build.sh`
   - Output Directory: `api`

2. **Set Environment Variables**
   - `TELEGRAM_BOT_TOKEN`
   - `WEBHOOK_URL` (will be available after deployment)

3. **Configure Build**
   - Install Command: `pip install -r requirements.txt`
   - Build Command: `bash vercel-build.sh`

4. **Deploy & Test**
   - Deploy project
   - Set webhook via `/set-webhook` endpoint
   - Test with `/start` command

## 🔍 Troubleshooting

### Bot Not Responding?
1. Check `/health` endpoint
2. Verify environment variables
3. Check `/debug` for errors
4. Ensure webhook is set correctly

### Playwright Issues?
1. Verify build script runs: `playwright install chromium`
2. Check `PLAYWRIGHT_BROWSERS_PATH` is set
3. Review build logs in Vercel dashboard

### Memory/Timeout Issues?
- Upgrade to Vercel Pro for more resources
- Optimize browser usage
- Use API endpoints instead of scraping

## 📈 Performance

- **Cold Start**: ~1-2 seconds
- **Webhook Response**: < 500ms
- **API Calls**: Cached for 24 hours
- **Live Timing**: 15-second refresh

## 🔐 Security

- Keep `TELEGRAM_BOT_TOKEN` secret
- Use Vercel environment variables
- Don't commit secrets to git
- Review webhook logs regularly

## 🛠️ Development

### Local Testing
```bash
# Install dependencies
pip install -r requirements.txt

# Set environment variables
export TELEGRAM_BOT_TOKEN="your_token"
export WEBHOOK_URL="https://your-project.vercel.app/webhook"

# Test webhook locally (requires ngrok)
ngrok http 8080
python app.py
```

### Vercel Dev
```bash
vercel dev
```

## 📚 Additional Resources

- [Full Deployment Guide](VERCEL_DEPLOYMENT_GUIDE.md)
- [Telegram Bot API](https://core.telegram.org/bots/api)
- [Vercel Python Documentation](https://vercel.com/docs/runtimes#official-runtimes/python)
- [OpenF1 API](https://openf1.org/)

## 🤝 Contributing

Contributions welcome! Please ensure:
- Code follows existing patterns
- Test on Vercel before submitting
- Update documentation for new features

## 📄 License

MIT License - feel free to use and modify.

---

**Ready to deploy?** Click the "Deploy with Vercel" button above or follow the [detailed deployment guide](VERCEL_DEPLOYMENT_GUIDE.md).