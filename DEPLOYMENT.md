# Deployment Guide for SSH Telegram Bot

## Deploy to Production Server (141.136.42.249)

### Prerequisites
- Ubuntu/Debian server with root access
- Python 3.8+ installed
- Git installed

### Step 1: Clone Repository on Server

```bash
# SSH into your server
ssh root@141.136.42.249

# Clone the repository
cd /opt
git clone https://github.com/thertxnetwork/ssh-telegram-bot.git
cd ssh-telegram-bot
```

### Step 2: Install Dependencies

```bash
# Update system packages
apt update && apt upgrade -y

# Install Python and pip if not already installed
apt install python3 python3-pip python3-venv -y

# Create virtual environment
python3 -m venv .venv

# Activate virtual environment
source .venv/bin/activate

# Install required packages
pip install -r requirements.txt
```

### Step 3: Configure Environment

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your bot token
nano .env
```

**Edit the .env file:**
```env
BOT_TOKEN=YOUR_TELEGRAM_BOT_TOKEN_HERE
ADMIN_IDS=  # Optional: comma-separated user IDs
LOG_LEVEL=INFO
LOG_FILE=/var/log/ssh_bot.log
MAX_CONNECTIONS_PER_USER=5
SESSION_TIMEOUT=3600
MAX_OUTPUT_LENGTH=4000
```

Save and exit (Ctrl+X, Y, Enter)

### Step 4: Create Systemd Service (Run as Service)

```bash
# Create systemd service file
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

[Install]
WantedBy=multi-user.target
EOF

# Reload systemd
systemctl daemon-reload

# Enable service to start on boot
systemctl enable ssh-telegram-bot

# Start the service
systemctl start ssh-telegram-bot

# Check status
systemctl status ssh-telegram-bot
```

### Step 5: Manage the Bot

```bash
# Start the bot
systemctl start ssh-telegram-bot

# Stop the bot
systemctl stop ssh-telegram-bot

# Restart the bot
systemctl restart ssh-telegram-bot

# View logs
journalctl -u ssh-telegram-bot -f

# Or check log file
tail -f /var/log/ssh_bot.log
```

### Step 6: Update Bot (Pull Latest Changes)

```bash
cd /opt/ssh-telegram-bot
git pull origin main
systemctl restart ssh-telegram-bot
```

## Alternative: Run with Screen (Quick Test)

If you want to test quickly without systemd:

```bash
# Install screen
apt install screen -y

# Start a screen session
screen -S ssh-bot

# Activate venv and run
cd /opt/ssh-telegram-bot
source .venv/bin/activate
python main.py

# Detach from screen: Ctrl+A, then D
# Reattach: screen -r ssh-bot
# Kill session: screen -X -S ssh-bot quit
```

## Firewall Configuration

If you have UFW enabled:

```bash
# Allow SSH (important!)
ufw allow 22/tcp

# Check status
ufw status
```

## Security Recommendations

1. **Use a dedicated user** (optional, instead of root):
```bash
useradd -r -s /bin/bash -d /opt/ssh-telegram-bot ssh-bot-user
chown -R ssh-bot-user:ssh-bot-user /opt/ssh-telegram-bot
# Update systemd service User=ssh-bot-user
```

2. **Restrict admin access**: Add specific user IDs to `ADMIN_IDS` in .env

3. **Monitor logs regularly**:
```bash
tail -f /var/log/ssh_bot.log
```

4. **Keep bot updated**:
```bash
cd /opt/ssh-telegram-bot
git pull
systemctl restart ssh-telegram-bot
```

## Troubleshooting

### Bot won't start
```bash
# Check logs
journalctl -u ssh-telegram-bot -n 50

# Check if port is blocked
netstat -tuln | grep 22

# Verify token
cat .env | grep BOT_TOKEN
```

### Connection issues
```bash
# Test internet connectivity
ping -c 3 api.telegram.org

# Check firewall
ufw status
iptables -L
```

### Permission errors
```bash
# Fix permissions
chown -R root:root /opt/ssh-telegram-bot
chmod +x main.py
```

## Quick Commands Reference

```bash
# One-line deployment (after repository is cloned)
cd /opt/ssh-telegram-bot && python3 -m venv .venv && source .venv/bin/activate && pip install -r requirements.txt && cp .env.example .env && echo "Now edit .env with your BOT_TOKEN"

# Start bot immediately (without systemd)
cd /opt/ssh-telegram-bot && source .venv/bin/activate && python main.py

# Check if running
ps aux | grep main.py
```

---

## Production Checklist

- [ ] Python 3.8+ installed
- [ ] Repository cloned to /opt/ssh-telegram-bot
- [ ] Virtual environment created and activated
- [ ] Dependencies installed from requirements.txt
- [ ] .env file configured with BOT_TOKEN
- [ ] Systemd service created and enabled
- [ ] Bot service started and running
- [ ] Logs accessible and monitoring set up
- [ ] Firewall configured (if applicable)
- [ ] Admin IDs configured (optional)

**Your bot is now running 24/7 on your server!** 🚀
