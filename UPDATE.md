# 🎉 Major Update - Enhanced SSH Telegram Bot

## Version 2.0 - Released October 24, 2025

### 🚀 New Features

#### 📂 **Advanced File Manager**
- **File Browsing** with emoji icons for different file types
  - 📁 Folders, 🐍 Python files, 📜 JavaScript, 🖼️ Images, etc.
- **File Operations**:
  - View, Edit, Download files
  - Create new files and folders
  - Rename, Copy, Move files
  - Delete files and folders
  - Change permissions (chmod)
  - View detailed file information
- **Pagination** for large directory listings
- **Smart Size Formatting** (B, KB, MB, GB, TB)
- **Navigate** easily with Home button and breadcrumbs

#### 📊 **System Monitoring**
- **System Information**:
  - Hostname, OS, Kernel version
  - System uptime
  - Active users count
- **Resource Usage**:
  - Real-time CPU usage percentage
  - Memory usage (used/total)
  - Disk usage for all partitions
  - System load average
- **Process Monitoring**:
  - Top processes by CPU usage
  - Full process list with details
- **Network Information**:
  - Network interfaces and IPs
  - Public IP address
  - Listening ports
  - Network statistics

#### ⚡ **Quick Commands Menu**
Instant access to common commands:
- `ls -la` - List files with details
- `pwd` - Print working directory
- `df -h` - Disk usage
- `ps aux` - Process list
- `ifconfig` - Network interfaces
- `top` - System monitor
- `free -h` - Memory usage
- `whoami` - Current user
- `systemctl` - Service management
- `journalctl` - System logs

#### 📄 **Enhanced Output Handling**
- **Pagination** for large command outputs
- Increased output limit from 4KB to 100KB
- **Page Navigation** with Previous/Next buttons
- Shows page numbers (e.g., "Page 1/5")
- Better formatting for file listings
- No more truncated `cat` command outputs!

#### 🎨 **Improved UI/UX**
- **Better Icons** - Emoji icons throughout the interface
- **Context Menus** - Smart menus based on current state
- **Cleaner Layout** - Organized button groups
- **Quick Access** - Faster navigation
- **Visual Feedback** - Clear status indicators
- **Breadcrumb Navigation** - Know where you are

### 🔧 **Technical Improvements**

#### Configuration Updates
- `MAX_OUTPUT_LENGTH`: Increased from 4,000 to 100,000 characters
- `OUTPUT_PAGE_SIZE`: 3,500 characters per page
- `SSH_CONNECT_TIMEOUT`: Increased from 10s to 30s
- `SSH_AUTH_TIMEOUT`: Increased from 10s to 30s
- `SSH_BANNER_TIMEOUT`: Increased from 10s to 30s

#### New Modules
- **`FileManager`** - Advanced file operations and browsing
- **`SystemMonitor`** - System statistics and monitoring
- **Enhanced Keyboards** - More menu options and navigation

#### Code Structure
```
utils/
├── file_manager.py      # NEW: File operations and utilities
├── system_monitor.py    # NEW: System monitoring functions
├── ssh_manager.py       # Enhanced with better error handling
├── session_manager.py   # User state management
└── helpers.py           # Utility functions

keyboards/
└── layouts.py           # ENHANCED: New menus and navigation

handlers/
├── commands.py          # Command handlers
└── callbacks.py         # Callback query handlers
```

### 📱 **New Menu Structure**

#### Main Menu (Connected)
- 📝 Execute Command
- 📂 File Manager | 📊 System Monitor
- ⚡ Quick Commands | ℹ️ Session Info
- 🔌 Disconnect

#### File Manager Menu
- 📋 Browse Files
- 📍 Current Dir | 🏠 Home
- 📤 Upload | 📥 Download
- ➕ New File | 📁 New Folder
- 💾 Disk Usage | 🔍 Search

#### System Monitor Menu
- 🖥️ System Info | 📊 Resources
- ⚙️ Top Processes | 💾 Disk Usage
- 🌐 Network | 🔌 Ports
- 🔄 Refresh All

#### Quick Commands Menu
- 📋 ls -la | 📍 pwd
- 💾 df -h | 🔍 ps aux
- 🌐 ifconfig | 🔝 top
- 📊 free -h | 👤 whoami
- 🔄 systemctl | 📝 journalctl

### 🎯 **Usage Examples**

#### Browse Files
1. Click "📂 File Manager"
2. Click "📋 Browse Files"
3. Navigate with ⬅️ Prev / ➡️ Next
4. Click any action button

#### Monitor System
1. Click "📊 System Monitor"
2. Choose what to view:
   - System Info
   - Resources (CPU, RAM, Disk)
   - Top Processes
   - Network details

#### Execute Quick Command
1. Click "⚡ Quick Commands"
2. Select command (e.g., "📋 ls -la")
3. View output with pagination

#### View Large Files
1. Run `cat large_file.txt`
2. Navigate pages with ⬅️ ➡️ buttons
3. Page indicator shows "📄 1/5"

### 🐛 **Bug Fixes**
- ✅ Fixed output truncation for large files
- ✅ Improved connection timeout handling
- ✅ Better error messages
- ✅ Enhanced session cleanup

### 🔄 **Breaking Changes**
None! This update is fully backward compatible.

### 📦 **Update Instructions**

#### For Running Instances
```bash
ssh root@141.136.42.249
cd /opt/ssh-telegram-bot
git pull origin main
systemctl restart ssh-telegram-bot
```

#### For New Deployments
```bash
git clone https://github.com/thertxnetwork/ssh-telegram-bot.git
cd ssh-telegram-bot
bash deploy.sh
```

### 🎁 **Coming Soon**
- Port forwarding
- Multiple simultaneous sessions
- Tunnel management
- File editor with syntax highlighting
- Custom command shortcuts
- Scheduled command execution
- Command history
- File search functionality
- Batch operations

### 📝 **Changelog**

**v2.0.0** (Oct 24, 2025)
- Added advanced file manager
- Added system monitoring
- Added quick commands menu
- Implemented output pagination
- Improved UI/UX
- Increased timeouts
- Better error handling

**v1.0.0** (Oct 24, 2025)
- Initial release
- Basic SSH connection
- Command execution
- File upload/download
- Session management

### 🙏 **Acknowledgments**
Built with ❤️ using:
- python-telegram-bot
- paramiko
- python-dotenv

### 📄 **License**
MIT License

---

**Enjoy the enhanced SSH Telegram Bot!** 🚀

For issues or suggestions: https://github.com/thertxnetwork/ssh-telegram-bot/issues
