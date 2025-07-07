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

# Activate virtualenv
source venv/bin/activate

# Install dependencies
pip install -r requirements.txt
#!/bin/bash

# Exit if any command fails
set -e

echo "🚀 Starting deployment..."

# Navigate to the project directory (edit if needed)
cd /root/content-agent

# Pull latest code from main branch
echo "🔄 Pulling latest code..."
git pull origin main

# Activate virtual environment
echo "🐍 Activating virtualenv..."
source venv/bin/activate

# Install dependencies
echo "📦 Installing Python dependencies..."
pip install -r requirements.txt

# Restart FastAPI app with PM2
echo "🔁 Restarting FastAPI app with PM2..."
pm2 restart content-agent || pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name content-agent

# Save PM2 state
pm2 save

echo "✅ Deployment complete."
