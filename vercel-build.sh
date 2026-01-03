#!/bin/bash
# Vercel build script for F1 Telegram Bot

echo "Building F1 Telegram Bot for Vercel..."

# Install Python dependencies
echo "Installing Python dependencies..."
pip install -r requirements.txt

# Install Playwright browsers
echo "Installing Playwright browsers..."
playwright install chromium --with-deps

# Create necessary directories
mkdir -p /tmp/playwright

echo "Build completed successfully!"