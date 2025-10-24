#!/bin/bash

echo "🚀 Installing dependencies..."

pip install -r requirements.txt

echo "⚙️ Installing Playwright browsers..."

python3 -m playwright install chromium

echo "✅ Starting Messenger E2EE Bot..."

python3 main.py
 





 