# F1 Bot Dockerfile for Leapcell Deployment
FROM python:3.11-slim

# Set working directory
WORKDIR /app

# Copy application files
COPY . .

# Install Python dependencies
RUN pip install --no-cache-dir -r requirements.txt

# Expose port
EXPOSE 8080

# Start command
CMD ["gunicorn", "-w", "1", "-b", ":8080", "app:app"]