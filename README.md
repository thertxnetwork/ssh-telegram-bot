# SSH Telegram Bot

A full-featured Telegram bot that provides a remote SSH terminal interface with proper navigation, error handling, and file management capabilities.

## Features

- 🔐 **Dual Authentication**: Connect using password or SSH private key
- 💻 **Command Execution**: Execute shell commands remotely
- 📂 **File Management**: Upload and download files to/from SSH server
- 🗂️ **Directory Navigation**: Navigate and manage directories
- 📱 **Inline Keyboards**: Easy navigation with interactive menus
- 🔄 **Session Management**: Automatic session cleanup and timeout handling
- 🛡️ **Security**: Credentials never stored, messages with passwords auto-deleted
- 📊 **Session Info**: Track connection status, duration, and current directory
- ⚠️ **Error Handling**: Comprehensive error handling and user-friendly messages

## Installation

### Prerequisites

- Python 3.8 or higher
- A Telegram Bot Token (get one from [@BotFather](https://t.me/BotFather))
- SSH server credentials to test the bot

### Setup

1. **Clone or download this repository**

2. **Install dependencies**
   ```bash
   pip install -r requirements.txt
   ```

3. **Configure environment variables**
   
   Copy `.env.example` to `.env`:
   ```bash
   cp .env.example .env
   ```
   
   Edit `.env` and add your bot token:
   ```env
   BOT_TOKEN=your_telegram_bot_token_here
   ```

4. **Run the bot**
   ```bash
   python main.py
   ```

## Usage

### Starting the Bot

1. Open your bot in Telegram
2. Send `/start` to begin
3. Choose "🔐 New Connection" from the menu

### Connecting to SSH Server

**Option 1: Password Authentication**
1. Select "🔑 Connect with Password"
2. Enter host (e.g., `example.com:22` or `192.168.1.100`)
3. Enter username
4. Enter password (message will be auto-deleted)

**Option 2: SSH Key Authentication**
1. Select "🔐 Connect with SSH Key"
2. Enter host and username
3. Send your private key file (e.g., `id_rsa`)

### Available Commands

- `/start` - Start the bot and show main menu
- `/help` - Show help information
- `/connect` - Start new SSH connection
- `/disconnect` - Close current SSH connection
- `/status` - Show connection status and info
- `/menu` - Show main menu

### Executing Commands

Once connected, simply type any shell command:
```
ls -la
pwd
cd /var/log
cat file.txt
top -n 1
df -h
```

### File Management

Use the "📂 File Manager" menu to:
- **List Files**: View files in current directory
- **Show Current Dir**: Display current working directory
- **Upload File**: Send a file to upload to the server
- **Download File**: Enter path to download a file

### Navigation

The bot uses inline keyboard menus for easy navigation:
- Main Menu: Access all features
- Connection Menu: Choose authentication method
- File Manager: File operations
- Session Info: View connection details
- Help Menu: Documentation and guides

## Project Structure

```
ssh-bot/
├── config/
│   ├── __init__.py
│   └── config.py          # Configuration and environment variables
├── handlers/
│   ├── __init__.py
│   ├── commands.py        # Command handlers (/start, /help, etc.)
│   └── callbacks.py       # Inline keyboard callback handlers
├── keyboards/
│   ├── __init__.py
│   └── layouts.py         # Inline keyboard layouts
├── models/
│   ├── __init__.py
│   └── session.py         # Data models for sessions and states
├── utils/
│   ├── __init__.py
│   ├── ssh_manager.py     # SSH connection management
│   ├── session_manager.py # User session state management
│   └── helpers.py         # Utility functions
├── .env.example           # Example environment variables
├── .gitignore
├── requirements.txt       # Python dependencies
├── main.py               # Main entry point
└── README.md             # This file
```

## Configuration

Edit `.env` file to customize:

```env
# Required
BOT_TOKEN=your_bot_token

# Optional
ADMIN_IDS=123456789,987654321  # Comma-separated admin user IDs
LOG_LEVEL=INFO                  # DEBUG, INFO, WARNING, ERROR
LOG_FILE=ssh_bot.log           # Log file path
MAX_CONNECTIONS_PER_USER=5     # Max concurrent connections
SESSION_TIMEOUT=3600           # Session timeout in seconds
MAX_OUTPUT_LENGTH=4000         # Max command output length
```

## Security Considerations

⚠️ **Important Security Notes:**

1. **Credentials**: Passwords and SSH keys are never stored permanently. They're only used to establish connections.
2. **Private Chat**: Always use the bot in a private chat, never in groups.
3. **Password Messages**: Messages containing passwords are automatically deleted.
4. **SSH Keys**: Private keys are processed in memory and discarded after use.
5. **Session Timeout**: Inactive sessions are automatically closed.
6. **Admin Only**: Consider restricting bot access using `ADMIN_IDS` in production.

## Error Handling

The bot includes comprehensive error handling:
- Connection timeouts
- Authentication failures
- Invalid commands
- File transfer errors
- Network issues
- Session expiration

All errors provide user-friendly messages with suggestions for resolution.

## Dependencies

- `python-telegram-bot` (20.7) - Telegram Bot API wrapper
- `paramiko` (3.4.0) - SSH implementation
- `python-dotenv` (1.0.0) - Environment variable management
- `cryptography` (41.0.7) - Cryptographic operations

## Troubleshooting

### Bot doesn't start
- Check if `BOT_TOKEN` is correctly set in `.env`
- Verify Python version is 3.8+
- Ensure all dependencies are installed

### Connection fails
- Verify SSH server is accessible
- Check firewall settings
- Confirm credentials are correct
- Ensure SSH port is correct (default: 22)

### Command execution issues
- Check if you have proper permissions on the server
- Verify the command syntax
- Some interactive commands may not work (e.g., vim, nano)

### File upload/download problems
- Check file size (max 50MB by default)
- Verify you have write permissions
- Ensure sufficient disk space

## Contributing

Feel free to submit issues, fork the repository, and create pull requests for any improvements.

## License

This project is open source and available under the MIT License.

## Disclaimer

This bot is for legitimate system administration purposes only. Always ensure you have proper authorization before connecting to any SSH server. The developers are not responsible for any misuse of this tool.

## Support

For issues, questions, or suggestions:
- Open an issue on GitHub
- Check the `/help` command in the bot
- Review the inline help menus

---

**Happy SSH-ing! 🚀**
