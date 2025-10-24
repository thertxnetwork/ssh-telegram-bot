# Quick Start Guide

## 1. Setup

```bash
# Install dependencies
pip install -r requirements.txt

# Configure environment
cp .env.example .env
# Edit .env and add your BOT_TOKEN
```

## 2. Run

```bash
python main.py
```

## 3. Use

1. Open bot in Telegram
2. Send `/start`
3. Click "🔐 New Connection"
4. Choose authentication method
5. Enter credentials
6. Start executing commands!

## Example Session

```
User: /start
Bot: Shows main menu

User: Clicks "New Connection" → "Connect with Password"
Bot: "Enter host..."

User: example.com:22
Bot: "Enter username..."

User: admin
Bot: "Enter password..."

User: [password]
Bot: "✅ Connected to example.com:22 as admin"

User: ls -la
Bot: [shows directory listing]

User: cd /var/www
Bot: "Changed directory to /var/www"

User: Clicks "File Manager" → "Upload File"
User: [sends file]
Bot: "✅ File uploaded to /var/www/file.txt"
```

## Common Commands

Once connected, try:
- `ls -la` - List files
- `pwd` - Current directory
- `cd /path` - Change directory
- `cat file.txt` - View file
- `df -h` - Disk usage
- `free -m` - Memory usage
- `ps aux` - Running processes
- `whoami` - Current user

## Tips

- Sessions auto-cleanup after 1 hour of inactivity
- Max output: 4000 characters (configurable)
- Upload limit: 50MB (configurable)
- Use inline keyboards for easy navigation
- Password messages are auto-deleted for security
