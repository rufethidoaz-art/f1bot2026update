# F1 Telegram Bot - Vercel Deployment Guide

This guide will help you deploy your F1 Telegram Bot to Vercel as a serverless application.

## 🚀 Quick Start

### Prerequisites
1. **Vercel Account**: Sign up at [vercel.com](https://vercel.com)
2. **Telegram Bot Token**: Get from [@BotFather](https://t.me/BotFather)
3. **Vercel CLI** (optional): `npm i -g vercel`

### Step 1: Prepare Your Repository

Your project structure should look like this:
```
f1-telegram-bot/
├── api/
│   ├── webhook.py          # Main webhook handler
│   ├── health.py           # Health check endpoint
│   ├── index.py            # Main endpoint
│   ├── debug.py            # Debug information
│   ├── webhook_info.py     # Webhook info
│   └── set_webhook.py      # Webhook setup
├── f1_bot_live.py          # Bot handlers (existing)
├── f1_playwright_scraper_fixed.py  # Scraper (existing)
├── requirements.txt        # Python dependencies
├── vercel.json             # Vercel configuration
├── package.json            # Build scripts
└── vercel-build.sh         # Build script
```

### Step 2: Deploy to Vercel

#### Option A: Using Vercel CLI
```bash
# Install Vercel CLI (if not already installed)
npm i -g vercel

# Login to Vercel
vercel login

# Deploy
vercel

# Follow the prompts:
# - Set project name
# - Link to GitHub repository (optional)
# - Configure environment variables
```

#### Option B: Using Vercel Dashboard
1. Go to [vercel.com/dashboard](https://vercel.com/dashboard)
2. Click "Add New" → "Project"
3. Import your GitHub repository
4. Configure project settings:
   - **Framework Preset**: Other
   - **Build Command**: `bash vercel-build.sh`
   - **Output Directory**: `api`
   - **Install Command**: `pip install -r requirements.txt`

### Step 3: Configure Environment Variables

In Vercel dashboard, go to Project Settings → Environment Variables and add:

| Variable | Description | Example |
|----------|-------------|---------|
| `TELEGRAM_BOT_TOKEN` | Your Telegram bot token | `123456:ABC-DEF1234ghIkl-zyx57W2v1u123ew11` |
| `WEBHOOK_URL` | Your Vercel webhook URL | `https://your-project.vercel.app/webhook` |

**Note**: Your webhook URL will be available after deployment in the format: `https://your-project.vercel.app/webhook`

### Step 4: Set Up Playwright (Important!)

Vercel requires Playwright browsers to be installed during build. The `vercel-build.sh` script handles this automatically.

If you encounter issues, you can also set these environment variables:
- `PLAYWRIGHT_BROWSERS_PATH=/tmp/playwright`
- `PLAYWRIGHT_SKIP_BROWSER_DOWNLOAD=0`

### Step 5: Configure Telegram Webhook

After deployment, you need to set your Telegram webhook. You have two options:

#### Option 1: Automatic Setup
Visit your webhook setup endpoint:
```
https://your-project.vercel.app/set-webhook
```

#### Option 2: Manual Setup
Use the Telegram Bot API:
```bash
curl -F "url=https://your-project.vercel.app/webhook" \
     https://api.telegram.org/bot<YOUR_BOT_TOKEN>/setWebhook
```

### Step 6: Test Your Bot

1. **Health Check**: Visit `https://your-project.vercel.app/health`
2. **Debug Info**: Visit `https://your-project.vercel.app/debug`
3. **Send a message**: Open Telegram and send `/start` to your bot

## 📋 API Endpoints

Your bot will provide these endpoints:

| Endpoint | Purpose |
|----------|---------|
| `/webhook` | Main Telegram webhook handler |
| `/health` | Health check endpoint |
| `/debug` | Debug information and status |
| `/webhook-info` | Webhook configuration info |
| `/set-webhook` | Webhook setup helper |
| `/` | Main info page |

## 🔧 Troubleshooting

### Common Issues

#### 1. Playwright Installation Fails
**Solution**: Ensure `vercel-build.sh` is executable and the build command is set correctly.

#### 2. Bot Not Responding
**Check**:
- Environment variables are set correctly
- Webhook URL is correct and accessible
- Bot token is valid

#### 3. Memory Issues
**Solution**: Vercel has memory limits. If using Playwright heavily, consider:
- Using the OpenF1 API instead of scraping
- Optimizing browser usage
- Using Vercel Pro plan for more resources

#### 4. Timeout Issues
**Solution**: 
- Increase timeout in Vercel settings (max 60s on Hobby plan)
- Use background functions for long-running tasks
- Optimize bot response times

## 📊 Monitoring

### Vercel Dashboard
- **Functions**: View serverless function invocations
- **Logs**: Real-time logs for debugging
- **Metrics**: Performance and usage statistics

### Telegram Bot Logs
Check `/debug` endpoint for:
- Bot initialization status
- Import status of modules
- Environment configuration

## 🔄 Updates & Redeployment

To update your bot:
```bash
git add .
git commit -m "Update bot functionality"
git push origin main
```

Vercel will automatically redeploy. Or manually trigger redeployment from dashboard.

## 💡 Performance Tips

1. **Use Caching**: The bot already implements caching for API responses
2. **Minimize Browser Usage**: Prefer API endpoints over scraping when possible
3. **Optimize Dependencies**: Only include necessary packages in requirements.txt
4. **Monitor Usage**: Keep an eye on Vercel usage limits

## 🆘 Support

If you encounter issues:
1. Check `/debug` endpoint for detailed error information
2. Review Vercel logs in dashboard
3. Verify environment variables are set correctly
4. Ensure Telegram bot token is valid and not expired

## 🎯 Next Steps

- [ ] Set up custom domain (optional)
- [ ] Configure monitoring and alerts
- [ ] Add rate limiting for production
- [ ] Implement backup webhook handlers
- [ ] Set up CI/CD pipeline

---

**Note**: This deployment is optimized for Vercel's serverless environment. Some features from the original Leapcell deployment may need adjustment for optimal performance.