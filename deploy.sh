#!/bin/bash
# Quick deployment script for SSH Telegram Bot
# Run this on your server: root@141.136.42.249

echo "=== SSH Telegram Bot - Quick Deployment ==="
echo ""

# Check if running as root
if [ "$EUID" -ne 0 ]; then 
    echo "Please run as root"
    exit 1
fi

# Update system
echo "Step 1: Updating system packages..."
apt update && apt upgrade -y

# Install dependencies
echo "Step 2: Installing Python and dependencies..."
apt install -y python3 python3-pip python3-venv git

# Clone repository
echo "Step 3: Cloning repository..."
cd /opt
if [ -d "ssh-telegram-bot" ]; then
    echo "Directory exists, pulling latest changes..."
    cd ssh-telegram-bot
    git pull
else
    git clone https://github.com/thertxnetwork/ssh-telegram-bot.git
    cd ssh-telegram-bot
fi

# Create virtual environment
echo "Step 4: Setting up Python virtual environment..."
python3 -m venv .venv
source .venv/bin/activate

# Install Python packages
echo "Step 5: Installing Python packages..."
pip install -r requirements.txt

# Configure environment
echo "Step 6: Configuring environment..."
if [ ! -f ".env" ]; then
    cp .env.example .env
    echo ""
    echo "⚠️  IMPORTANT: Edit .env file and add your BOT_TOKEN"
    echo "Run: nano .env"
    echo ""
    read -p "Press Enter after you've configured .env..."
fi

# Create systemd service
echo "Step 7: Creating systemd service..."
cat > /etc/systemd/system/ssh-telegram-bot.service << 'EOF'
[Unit]
Description=SSH Telegram Bot
After=network.target

[Service]
Type=simple
User=root
WorkingDirectory=/opt/ssh-telegram-bot
Environment="PATH=/opt/ssh-telegram-bot/.venv/bin"
ExecStart=/opt/ssh-telegram-bot/.venv/bin/python main.py
Restart=always
RestartSec=10
StandardOutput=journal
StandardError=journal

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd and enable service
systemctl daemon-reload
systemctl enable ssh-telegram-bot

# Start the bot
echo "Step 8: Starting the bot..."
systemctl start ssh-telegram-bot

# Wait a moment
sleep 2

# Check status
echo ""
echo "=== Bot Status ==="
systemctl status ssh-telegram-bot --no-pager

echo ""
echo "=== Deployment Complete! ==="
echo ""
echo "Useful commands:"
echo "  - View logs:        journalctl -u ssh-telegram-bot -f"
echo "  - Restart bot:      systemctl restart ssh-telegram-bot"
echo "  - Stop bot:         systemctl stop ssh-telegram-bot"
echo "  - Check status:     systemctl status ssh-telegram-bot"
echo "  - View log file:    tail -f /var/log/ssh_bot.log"
echo ""
echo "Bot is now running! Test it in Telegram."
