#!/bin/bash

echo "🔄 Pulling latest changes from Git..."
git pull origin main

echo "🐍 Activating virtual environment..."
source venv/bin/activate

echo "📦 Installing dependencies..."
pip install -r requirements.txt

echo "🚀 Restarting FastAPI app with PM2..."
pm2 restart content-agent

echo "💾 Saving PM2 process list..."
pm2 save

echo "✅ Deployment complete."
