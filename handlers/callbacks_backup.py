"""Callback query handlers for inline keyboard interactions."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from keyboards import Keyboards
from utils import SSHManager, SessionManager

logger = logging.getLogger(__name__)


class CallbackHandlers:
    """Handlers for inline keyboard callback queries."""
    
    def __init__(self, ssh_manager: SSHManager, session_manager: SessionManager):
        """
        Initialize callback handlers.
        
        Args:
            ssh_manager: SSH connection manager
            session_manager: User session manager
        """
        self.ssh = ssh_manager
        self.sessions = session_manager
    
    async def handle_callback(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Main callback query handler that routes to specific handlers."""
        query = update.callback_query
        await query.answer()
        
        user_id = query.from_user.id
        data = query.data
        
        logger.info(f"Callback from user {user_id}: {data}")
        
        # Route to appropriate handler
        if data == "menu_main":
            await self._show_main_menu(query, user_id)
        elif data == "menu_connect":
            await self._show_connect_menu(query, user_id)
        elif data == "menu_execute":
            await self._show_execute_prompt(query, user_id)
        elif data == "menu_files":
            await self._show_file_manager(query, user_id)
        elif data == "menu_info":
            await self._show_session_info(query, user_id)
        elif data == "menu_help":
            await self._show_help_menu(query, user_id)
        elif data == "connect_password":
            await self._start_password_connect(query, user_id)
        elif data == "connect_key":
            await self._start_key_connect(query, user_id)
        elif data == "action_disconnect":
            await self._disconnect(query, user_id)
        elif data == "file_list":
            await self._list_files(query, user_id)
        elif data == "file_pwd":
            await self._show_current_dir(query, user_id)
        elif data == "file_upload":
            await self._prompt_upload(query, user_id)
        elif data == "file_download":
            await self._prompt_download(query, user_id)
        elif data == "help_commands":
            await self._show_commands_help(query, user_id)
        elif data == "help_ssh_key":
            await self._show_ssh_key_help(query, user_id)
        else:
            await query.edit_message_text(
                "⚠️ Unknown action.",
                reply_markup=Keyboards.main_menu(self.ssh.is_connected(user_id))
            )
    
    async def _show_main_menu(self, query, user_id: int):
        """Show main menu."""
        is_connected = self.ssh.is_connected(user_id)
        self.sessions.reset_state(user_id)
        
        await query.edit_message_text(
            "📱 **Main Menu**\n\n" + 
            ("✅ SSH connection active" if is_connected else "❌ No active connection"),
            reply_markup=Keyboards.main_menu(is_connected),
            parse_mode='Markdown'
        )
    
    async def _show_connect_menu(self, query, user_id: int):
        """Show connection menu."""
        if self.ssh.is_connected(user_id):
            session = self.ssh.get_session(user_id)
            await query.edit_message_text(
                f"⚠️ Already connected to `{session.host}`.\n"
                "Disconnect first to create a new connection.",
                reply_markup=Keyboards.main_menu(True),
                parse_mode='Markdown'
            )
            return
        
        await query.edit_message_text(
            "🔐 **New SSH Connection**\n\n"
            "Choose your authentication method:",
            reply_markup=Keyboards.connection_menu(),
            parse_mode='Markdown'
        )
    
    async def _show_execute_prompt(self, query, user_id: int):
        """Prompt for command execution."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        self.sessions.set_state(user_id, 'awaiting_command')
        
        await query.edit_message_text(
            "📝 **Execute Command**\n\n"
            "Type the command you want to execute on the SSH server:",
            reply_markup=Keyboards.back_to_main(),
            parse_mode='Markdown'
        )
    
    async def _show_file_manager(self, query, user_id: int):
        """Show file manager menu."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        session = self.ssh.get_session(user_id)
        
        await query.edit_message_text(
            "📂 **File Manager**\n\n"
            f"Current directory: `{session.current_directory}`",
            reply_markup=Keyboards.file_manager_menu(),
            parse_mode='Markdown'
        )
    
    async def _show_session_info(self, query, user_id: int):
        """Show session information."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        session = self.ssh.get_session(user_id)
        
        # Calculate connection duration
        duration = ""
        if session.connected_at:
            from datetime import datetime
            delta = datetime.now() - session.connected_at
            hours, remainder = divmod(int(delta.total_seconds()), 3600)
            minutes, seconds = divmod(remainder, 60)
            duration = f"{hours}h {minutes}m {seconds}s"
        
        info_text = (
            "📊 **SSH Connection Status**\n\n"
            f"🌐 **Host:** `{session.host}:{session.port}`\n"
            f"👤 **User:** `{session.username}`\n"
            f"📂 **Directory:** `{session.current_directory}`\n"
            f"⏱️ **Connected:** {duration}\n"
            f"🔑 **Session ID:** `{session.session_id}`"
        )
        
        await query.edit_message_text(
            info_text,
            reply_markup=Keyboards.session_info_menu(),
            parse_mode='Markdown'
        )
    
    async def _show_help_menu(self, query, user_id: int):
        """Show help menu."""
        help_text = (
            "❓ **Help & Information**\n\n"
            "Select a topic below to learn more:"
        )
        
        await query.edit_message_text(
            help_text,
            reply_markup=Keyboards.help_menu(),
            parse_mode='Markdown'
        )
    
    async def _start_password_connect(self, query, user_id: int):
        """Start password-based connection."""
        self.sessions.set_state(user_id, 'awaiting_host', auth_method='password')
        
        await query.edit_message_text(
            "🔐 **Connect with Password**\n\n"
            "Please enter the SSH server address:\n"
            "Format: `hostname:port` or just `hostname` (default port 22)\n\n"
            "Example: `example.com:2222` or `192.168.1.100`",
            reply_markup=Keyboards.back_to_main(),
            parse_mode='Markdown'
        )
    
    async def _start_key_connect(self, query, user_id: int):
        """Start SSH key-based connection."""
        self.sessions.set_state(user_id, 'awaiting_host', auth_method='key')
        
        await query.edit_message_text(
            "🔐 **Connect with SSH Key**\n\n"
            "Please enter the SSH server address:\n"
            "Format: `hostname:port` or just `hostname` (default port 22)\n\n"
            "Example: `example.com:2222` or `192.168.1.100`",
            reply_markup=Keyboards.back_to_main(),
            parse_mode='Markdown'
        )
    
    async def _disconnect(self, query, user_id: int):
        """Disconnect from SSH server."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "⚠️ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        success, message = self.ssh.disconnect(user_id)
        self.sessions.reset_state(user_id)
        
        await query.edit_message_text(
            message,
            reply_markup=Keyboards.main_menu(False)
        )
    
    async def _list_files(self, query, user_id: int):
        """List files in current directory."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        # Execute ls command
        success, stdout, stderr = self.ssh.execute_command(user_id, "ls -lah")
        
        from utils import format_output
        output = format_output(stdout, stderr)
        
        await query.edit_message_text(
            f"📋 **File List**\n\n{output}",
            reply_markup=Keyboards.back_to_files(),
            parse_mode='Markdown'
        )
    
    async def _show_current_dir(self, query, user_id: int):
        """Show current directory."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        session = self.ssh.get_session(user_id)
        
        await query.edit_message_text(
            f"📍 **Current Directory**\n\n`{session.current_directory}`",
            reply_markup=Keyboards.back_to_files(),
            parse_mode='Markdown'
        )
    
    async def _prompt_upload(self, query, user_id: int):
        """Prompt for file upload."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        self.sessions.set_state(user_id, 'awaiting_file_upload')
        session = self.ssh.get_session(user_id)
        
        await query.edit_message_text(
            "📤 **Upload File**\n\n"
            f"Send a file to upload to: `{session.current_directory}`\n\n"
            "The file will be uploaded with its original name.",
            reply_markup=Keyboards.back_to_files(),
            parse_mode='Markdown'
        )
    
    async def _prompt_download(self, query, user_id: int):
        """Prompt for file download."""
        if not self.ssh.is_connected(user_id):
            await query.edit_message_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        self.sessions.set_state(user_id, 'awaiting_download_path')
        
        await query.edit_message_text(
            "📥 **Download File**\n\n"
            "Enter the path to the file you want to download:\n"
            "You can use absolute paths or relative to current directory.\n\n"
            "Example: `document.txt` or `/home/user/file.pdf`",
            reply_markup=Keyboards.back_to_files(),
            parse_mode='Markdown'
        )
    
    async def _show_commands_help(self, query, user_id: int):
        """Show commands help."""
        commands_text = (
            "📖 **Available Commands**\n\n"
            "**Bot Commands:**\n"
            "/start - Start the bot\n"
            "/help - Show help\n"
            "/connect - New SSH connection\n"
            "/disconnect - Close connection\n"
            "/status - Connection status\n"
            "/menu - Show main menu\n\n"
            "**When Connected:**\n"
            "Simply type any shell command to execute it.\n\n"
            "**Examples:**\n"
            "`ls -la` - List files\n"
            "`pwd` - Print working directory\n"
            "`cd /path` - Change directory\n"
            "`cat file.txt` - View file\n"
            "`top` - System monitor\n"
            "`df -h` - Disk usage"
        )
        
        await query.edit_message_text(
            commands_text,
            reply_markup=Keyboards.back_to_main(),
            parse_mode='Markdown'
        )
    
    async def _show_ssh_key_help(self, query, user_id: int):
        """Show SSH key setup help."""
        key_help_text = (
            "🔐 **SSH Key Authentication**\n\n"
            "**Generating SSH Key Pair:**\n"
            "1. On your computer, run:\n"
            "   `ssh-keygen -t rsa -b 4096`\n\n"
            "2. Copy public key to server:\n"
            "   `ssh-copy-id user@host`\n\n"
            "3. Or manually add to server:\n"
            "   Append public key to `~/.ssh/authorized_keys`\n\n"
            "**Using with Bot:**\n"
            "1. Choose 'Connect with SSH Key'\n"
            "2. Enter host and username\n"
            "3. Send your PRIVATE key file\n"
            "   (id_rsa, NOT id_rsa.pub)\n\n"
            "⚠️ **Security:**\n"
            "Keys are never stored, only used for connection."
        )
        
        await query.edit_message_text(
            key_help_text,
            reply_markup=Keyboards.back_to_main(),
            parse_mode='Markdown'
        )
