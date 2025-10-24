# GitHub Push Instructions

## You need to authenticate to push to GitHub

### Option 1: Using GitHub CLI (Recommended)

1. Install GitHub CLI: https://cli.github.com/
2. Run:
```powershell
gh auth login
git push -u origin main
```

### Option 2: Using Personal Access Token

1. Go to: https://github.com/settings/tokens
2. Click "Generate new token (classic)"
3. Select scopes: `repo` (all)
4. Copy the token
5. Push using token:

```powershell
git push https://YOUR_TOKEN@github.com/thertxnetwork/ssh-telegram-bot.git main
```

### Option 3: Using SSH Key

1. Generate SSH key (if you don't have one):
```powershell
ssh-keygen -t ed25519 -C "your_email@example.com"
```

2. Add to GitHub: https://github.com/settings/keys

3. Change remote to SSH:
```powershell
git remote set-url origin git@github.com:thertxnetwork/ssh-telegram-bot.git
git push -u origin main
```

### After Successful Push

The code will be available at:
https://github.com/thertxnetwork/ssh-telegram-bot

## Deploy to Server (141.136.42.249)

Once pushed to GitHub, connect to your server and run:

```bash
ssh root@141.136.42.249

# Quick deployment
cd /opt
git clone https://github.com/thertxnetwork/ssh-telegram-bot.git
cd ssh-telegram-bot
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
nano .env  # Add your BOT_TOKEN

# Run the bot
python main.py

# Or use systemd service (see DEPLOYMENT.md for full setup)
```

See **DEPLOYMENT.md** for complete production deployment instructions.
