#!/bin/bash

# Exit if any command fails
set -e

echo "🚀 Starting deployment to 159.203.99.128..."

echo "🔄 Pulling latest changes from Git..."
git pull origin main

echo "📦 Creating deployment package..."
tar -czf legal-leaflet-agent.tar.gz main.py requirements.txt frontend.html

echo "📤 Uploading to droplet..."
scp legal-leaflet-agent.tar.gz root@159.203.99.128:/root/

# SSH into droplet and run deployment commands
ssh root@159.203.99.128 << 'ENDSSH'

echo "📦 Installing system dependencies..."
apt update && apt install -y python3-pip python3-venv git nginx pm2

# Create application directory and set permissions
mkdir -p /root/legal-leaflet-agent
tar -xzf legal-leaflet-agent.tar.gz -C /root/legal-leaflet-agent

echo "🐍 Setting up Python environment..."
cd /root/legal-leaflet-agent
python3 -m venv venv
source venv/bin/activate
pip install -r requirements.txt

# Create .env file
echo "Creating .env file..."
echo "OPENAI_API_KEY=your_openai_key_here" > .env
echo "API_KEY=your_api_key_here" >> .env

echo "🔧 Configuring nginx..."
cat > /etc/nginx/sites-available/legal-leaflet-agent << 'EOL'
server {
    listen 80;
    server_name 159.203.99.128;

    location / {
        proxy_pass http://127.0.0.1:8000;
        proxy_set_header Host $host;
        proxy_set_header X-Real-IP $remote_addr;
        proxy_set_header X-Forwarded-For $proxy_add_x_forwarded_for;
        proxy_set_header X-Forwarded-Proto $scheme;
    }
}
EOL

ln -sf /etc/nginx/sites-available/legal-leaflet-agent /etc/nginx/sites-enabled/
nginx -t
systemctl restart nginx

# Start the application with PM2
echo "🚀 Starting application with PM2..."
pm2 start "uvicorn main:app --host 0.0.0.0 --port 8000" --name legal-leaflet-agent
pm2 save

ENDSSH

echo "✅ Deployment complete!"
echo "Access your application at: http://159.203.99.128"
echo "Note: Replace 'your_openai_key_here' and 'your_api_key_here' with your actual keys in the .env file on the droplet."

# Clean up
echo "🧹 Cleaning up..."
rm legal-leaflet-agent.tar.gz
