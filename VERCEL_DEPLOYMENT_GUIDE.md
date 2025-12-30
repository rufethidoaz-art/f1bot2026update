# F1 Bot Leapcell Deployment Guide

## Fix for Deployment Error

The deployment error occurs because the build command is being incorrectly interpreted. The error shows:

```
build_cmd_cYldi6pjRbR6khgWoA3Z.sh: 6: RUN: not found
```

This happens when the deployment system tries to execute `RUN playwright install` as a shell command, but `RUN` is a Docker instruction.

## Solution

### 1. Fixed leapcell.yaml

The `leapcell.yaml` file should only contain:

```yaml
runtime: python
build_command: pip install -r requirements.txt
start_command: gunicorn -w 1 -b :8080 app:app
port: 8080
```

**Important:** Do NOT include `RUN playwright install` in the build command. The `RUN` instruction is for Dockerfiles, not shell commands.

### 2. Requirements.txt

The `requirements.txt` should only include Python packages, not system commands:

```txt
python-telegram-bot==20.7
flask==3.0.3
requests==2.32.3
gunicorn==21.2.0
python-dotenv==1.0.1
flask[async]==3.0.3
```

### 3. Why Playwright is Not Needed

The F1 bot uses the `f1_bot_live.py` version which:
- Uses web scraping for live timing data
- Does NOT require Playwright browser automation
- Is optimized for serverless environments like Leapcell
- Has faster cold start times

### 4. Deployment Steps

1. Ensure `leapcell.yaml` contains only the correct build command
2. Verify `requirements.txt` has no system dependencies
3. Deploy using the Leapcell platform
4. The bot should start successfully without Docker build errors

### 5. Alternative: Manual Dockerfile

If the platform still has issues, you can create a `Dockerfile`:

```dockerfile
FROM python:3.11-slim

WORKDIR /app
COPY . .
RUN pip install -r requirements.txt

EXPOSE 8080
CMD ["gunicorn", "-w", "1", "-b", ":8080", "app:app"]
```

Then update `leapcell.yaml`:

```yaml
runtime: docker
build_command: docker build -t f1-bot .
start_command: docker run -p 8080:8080 f1-bot
port: 8080
```

## Troubleshooting

### Error: "RUN: not found"
- **Cause**: Deployment system interpreting Docker instructions as shell commands
- **Fix**: Use only shell commands in `build_command`, not Docker instructions

### Error: Missing dependencies
- **Cause**: Requirements.txt missing packages
- **Fix**: Ensure all Python packages are listed in requirements.txt

### Error: Port binding issues
- **Cause**: Incorrect port configuration
- **Fix**: Use port 8080 as specified in the configuration

## Testing

After deployment:
1. Check the health endpoint: `https://your-app.leapcell.io/health`
2. Verify the bot responds to webhook calls
3. Test basic functionality through Telegram