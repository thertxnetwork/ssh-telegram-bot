# Changelog

## [Latest Update] - October 25, 2025

### Fixed
- **Nano/Vim Issue**: Replaced interactive terminal editors with inline file editor
  - Uses `cat` for reading files
  - Uses `echo` and `tee` for writing files
  - Works perfectly over SSH exec_command
  - Supports files up to 50KB
  - Shows file info (size, permissions, owner)
  - Creates automatic backup before editing

### Added
- **Session Persistence**: Sessions now survive bot restarts
  - Saves sessions to `sessions.json` (excluded from git)
  - Auto-reconnects on bot startup
  - Saves host, port, username, password, current directory
  - Updates on directory changes
  - No more lost connections during bot updates!

- **File Editor Features**:
  - `📝 Edit File` button in file manager
  - View file contents with syntax info
  - Edit text files inline
  - Send new content as text message
  - Automatic validation (text files only)
  - File type detection (mime-type checking)
  - Paginated view for large files
  - Cancel editing without changes

### Technical Details

#### New Files Created:
- `utils/file_editor.py` - File editing utilities (170 lines)
- `utils/session_persistence.py` - Session storage/restore (134 lines)

#### Modified Files:
- `handlers/callbacks.py` - Added file edit callbacks (+172 lines)
- `handlers/commands.py` - Added file edit handlers (+115 lines)
- `utils/ssh_manager.py` - Integrated session persistence (+72 lines)
- `main.py` - Added session restoration on startup (+4 lines)
- `.gitignore` - Excluded sessions.json for security

#### How It Works:

**File Editing**:
1. User clicks "📝 Edit File" in File Manager
2. Enters filename or selects from browser
3. Bot reads file using `cat` command
4. Displays content with file info
5. User sends new content as text
6. Bot creates backup and writes using `printf > file`
7. Confirms save with file size

**Session Persistence**:
1. When user connects: Save to `sessions.json`
2. On directory change: Update `sessions.json`
3. On bot restart: Load `sessions.json`
4. Auto-reconnect to all saved sessions
5. Restore current directory for each session
6. Remove invalid sessions if reconnect fails

### User Benefits
✅ No more "nano not working" errors
✅ Edit files directly through Telegram
✅ Sessions survive bot updates/restarts
✅ Users don't lose active connections
✅ Automatic backups prevent data loss
✅ Works with all text files (Python, JSON, config, etc.)

### Security Notes
- `sessions.json` contains passwords (consider encryption for production)
- File excluded from git via `.gitignore`
- Only text files can be edited (binary files protected)
- File size limit: 50KB for editing
- Automatic backup created before changes

## Previous Updates

### October 24, 2025
- Implemented all missing callback handlers
- Added file manager with pagination
- Added system monitoring features
- Added quick commands menu
- Enhanced keyboard layouts
- Fixed output truncation issues

### Initial Release
- SSH connection with password/key authentication
- Command execution
- File upload/download
- Session management
- Inline keyboard navigation
