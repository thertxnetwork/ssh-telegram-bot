"""Command handlers for the SSH Telegram Bot."""
import logging
from telegram import Update
from telegram.ext import ContextTypes

from keyboards import Keyboards
from utils import SSHManager, SessionManager

logger = logging.getLogger(__name__)


class CommandHandlers:
    """Handlers for bot commands."""
    
    def __init__(self, ssh_manager: SSHManager, session_manager: SessionManager):
        """
        Initialize command handlers.
        
        Args:
            ssh_manager: SSH connection manager
            session_manager: User session manager
        """
        self.ssh = ssh_manager
        self.sessions = session_manager
    
    async def start_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /start command."""
        user = update.effective_user
        user_id = user.id
        
        logger.info(f"User {user_id} ({user.username}) started the bot")
        
        # Reset user state
        self.sessions.reset_state(user_id)
        
        welcome_message = (
            f"👋 Welcome to **SSH Terminal Bot**, {user.first_name}!\n\n"
            "🔐 I can help you manage your SSH connections and execute commands remotely.\n\n"
            "**Features:**\n"
            "• Connect to SSH servers with password or key\n"
            "• Execute shell commands\n"
            "• Upload and download files\n"
            "• Navigate directories\n"
            "• Session management\n\n"
            "Use the menu below to get started!"
        )
        
        is_connected = self.ssh.is_connected(user_id)
        await update.message.reply_text(
            welcome_message,
            reply_markup=Keyboards.main_menu(is_connected),
            parse_mode='Markdown'
        )
    
    async def help_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /help command."""
        help_text = (
            "📚 **SSH Terminal Bot - Help**\n\n"
            "**Available Commands:**\n"
            "/start - Start the bot and show main menu\n"
            "/help - Show this help message\n"
            "/connect - Start new SSH connection\n"
            "/disconnect - Close current SSH connection\n"
            "/status - Show current connection status\n"
            "/menu - Show main menu\n\n"
            "**Quick Tips:**\n"
            "• Use inline buttons for easy navigation\n"
            "• Send commands directly when connected\n"
            "• Upload files by sending documents\n"
            "• Sessions timeout after inactivity\n\n"
            "**Security Notice:**\n"
            "⚠️ Your credentials are never stored permanently.\n"
            "Always use this bot in a private chat."
        )
        
        await update.message.reply_text(
            help_text,
            reply_markup=Keyboards.back_to_main(),
            parse_mode='Markdown'
        )
    
    async def connect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /connect command."""
        user_id = update.effective_user.id
        
        if self.ssh.is_connected(user_id):
            session = self.ssh.get_session(user_id)
            await update.message.reply_text(
                f"⚠️ You are already connected to `{session.host}`.\n"
                f"Disconnect first or use the menu to manage your connection.",
                reply_markup=Keyboards.main_menu(True),
                parse_mode='Markdown'
            )
            return
        
        await update.message.reply_text(
            "🔐 **New SSH Connection**\n\n"
            "Choose your authentication method:",
            reply_markup=Keyboards.connection_menu(),
            parse_mode='Markdown'
        )
    
    async def disconnect_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /disconnect command."""
        user_id = update.effective_user.id
        
        if not self.ssh.is_connected(user_id):
            await update.message.reply_text(
                "⚠️ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        success, message = self.ssh.disconnect(user_id)
        self.sessions.reset_state(user_id)
        
        await update.message.reply_text(
            message,
            reply_markup=Keyboards.main_menu(False)
        )
    
    async def status_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /status command."""
        user_id = update.effective_user.id
        
        if not self.ssh.is_connected(user_id):
            await update.message.reply_text(
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
        
        status_text = (
            "📊 **SSH Connection Status**\n\n"
            f"🌐 **Host:** `{session.host}:{session.port}`\n"
            f"👤 **User:** `{session.username}`\n"
            f"📂 **Directory:** `{session.current_directory}`\n"
            f"⏱️ **Connected:** {duration}\n"
            f"🔑 **Session ID:** `{session.session_id}`"
        )
        
        await update.message.reply_text(
            status_text,
            reply_markup=Keyboards.session_info_menu(),
            parse_mode='Markdown'
        )
    
    async def menu_command(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle /menu command."""
        user_id = update.effective_user.id
        is_connected = self.ssh.is_connected(user_id)
        
        await update.message.reply_text(
            "📱 **Main Menu**",
            reply_markup=Keyboards.main_menu(is_connected),
            parse_mode='Markdown'
        )
    
    async def handle_message(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle text messages (commands or state-based input)."""
        user_id = update.effective_user.id
        text = update.message.text
        user_state = self.sessions.get_user_state(user_id)
        
        # Check if user is in a special state
        if user_state.state == "awaiting_host":
            await self._handle_host_input(update, context, text)
        elif user_state.state == "awaiting_username":
            await self._handle_username_input(update, context, text)
        elif user_state.state == "awaiting_password":
            await self._handle_password_input(update, context, text)
        elif user_state.state == "awaiting_command":
            await self._handle_command_input(update, context, text)
        elif user_state.state == "awaiting_download_path":
            await self._handle_download_path(update, context, text)
        elif user_state.state == "awaiting_file_to_edit":
            await self._handle_file_to_edit(update, context, text)
        elif user_state.state == "editing_file":
            await self._handle_file_content_edit(update, context, text)
        elif user_state.state == "connected" and self.ssh.is_connected(user_id):
            # Execute command if connected
            await self._handle_command_input(update, context, text)
        else:
            # Default response
            await update.message.reply_text(
                "ℹ️ Use /start to begin or /help for available commands.",
                reply_markup=Keyboards.main_menu(self.ssh.is_connected(user_id))
            )
    
    async def _handle_host_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle host input during connection setup."""
        user_id = update.effective_user.id
        
        # Parse host and port
        parts = text.split(':')
        host = parts[0].strip()
        port = int(parts[1]) if len(parts) > 1 and parts[1].strip().isdigit() else 22
        
        from utils import validate_host, validate_port
        
        if not validate_host(host):
            await update.message.reply_text(
                "❌ Invalid hostname or IP address. Please try again:",
                reply_markup=Keyboards.back_to_main()
            )
            return
        
        if not validate_port(port):
            await update.message.reply_text(
                "❌ Invalid port number (1-65535). Please try again:",
                reply_markup=Keyboards.back_to_main()
            )
            return
        
        # Store host and port
        self.sessions.set_temp_data(user_id, 'host', host)
        self.sessions.set_temp_data(user_id, 'port', port)
        self.sessions.set_state(user_id, 'awaiting_username')
        
        await update.message.reply_text(
            f"✅ Host: `{host}:{port}`\n\n"
            "👤 Please enter your SSH username:",
            reply_markup=Keyboards.back_to_main(),
            parse_mode='Markdown'
        )
    
    async def _handle_username_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle username input during connection setup."""
        user_id = update.effective_user.id
        username = text.strip()
        
        if not username:
            await update.message.reply_text(
                "❌ Username cannot be empty. Please try again:",
                reply_markup=Keyboards.back_to_main()
            )
            return
        
        # Store username
        self.sessions.set_temp_data(user_id, 'username', username)
        
        # Check if using key or password
        auth_method = self.sessions.get_temp_data(user_id, 'auth_method', 'password')
        
        if auth_method == 'key':
            self.sessions.set_state(user_id, 'awaiting_key')
            await update.message.reply_text(
                f"✅ Username: `{username}`\n\n"
                "🔐 Please send your private key file (as a document):",
                reply_markup=Keyboards.back_to_main(),
                parse_mode='Markdown'
            )
        else:
            self.sessions.set_state(user_id, 'awaiting_password')
            await update.message.reply_text(
                f"✅ Username: `{username}`\n\n"
                "🔑 Please enter your SSH password:\n"
                "⚠️ The message will be deleted after processing for security.",
                reply_markup=Keyboards.back_to_main(),
                parse_mode='Markdown'
            )
    
    async def _handle_password_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle password input and establish connection."""
        user_id = update.effective_user.id
        password = text
        
        # Delete the password message immediately
        try:
            await update.message.delete()
        except Exception as e:
            logger.warning(f"Could not delete password message: {e}")
        
        # Get connection details
        host = self.sessions.get_temp_data(user_id, 'host')
        port = self.sessions.get_temp_data(user_id, 'port', 22)
        username = self.sessions.get_temp_data(user_id, 'username')
        
        # Show connecting message
        status_msg = await context.bot.send_message(
            chat_id=user_id,
            text=f"🔄 Connecting to `{host}:{port}` as `{username}`...",
            parse_mode='Markdown'
        )
        
        # Attempt connection
        success, message = self.ssh.create_connection(
            user_id=user_id,
            host=host,
            port=port,
            username=username,
            password=password
        )
        
        # Update status message
        await status_msg.edit_text(
            message,
            reply_markup=Keyboards.main_menu(success),
            parse_mode='Markdown'
        )
        
        if success:
            self.sessions.set_state(user_id, 'connected')
        
        # Clear temporary data
        self.sessions.clear_temp_data(user_id)
    
    async def _handle_command_input(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle command execution."""
        user_id = update.effective_user.id
        
        if not self.ssh.is_connected(user_id):
            await update.message.reply_text(
                "❌ No active SSH connection. Please connect first.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        command = text.strip()
        
        # Show executing message
        status_msg = await update.message.reply_text(f"⚙️ Executing: `{command}`...", parse_mode='Markdown')
        
        # Execute command
        success, stdout, stderr = self.ssh.execute_command(user_id, command)
        
        from utils import format_output
        output = format_output(stdout, stderr)
        
        # Update message with result
        try:
            await status_msg.edit_text(
                f"💻 `{command}`\n\n{output}",
                parse_mode='Markdown',
                reply_markup=Keyboards.main_menu(True)
            )
        except Exception as e:
            # If message is too long, send as new message
            await status_msg.delete()
            await update.message.reply_text(
                f"💻 `{command}`\n\n{output[:4000]}",
                parse_mode='Markdown',
                reply_markup=Keyboards.main_menu(True)
            )
    
    async def _handle_download_path(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle file download path input."""
        user_id = update.effective_user.id
        remote_path = text.strip()
        
        if not self.ssh.is_connected(user_id):
            await update.message.reply_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            self.sessions.reset_state(user_id)
            return
        
        # Show downloading message
        status_msg = await update.message.reply_text(
            f"📥 Downloading `{remote_path}`...",
            parse_mode='Markdown'
        )
        
        # Download file
        success, file_data, message = self.ssh.download_file(user_id, remote_path)
        
        if success and file_data:
            from utils import get_filename_from_path
            filename = get_filename_from_path(remote_path)
            
            await status_msg.delete()
            await update.message.reply_document(
                document=file_data,
                filename=filename,
                caption=f"✅ Downloaded: `{remote_path}`",
                parse_mode='Markdown',
                reply_markup=Keyboards.back_to_files()
            )
        else:
            await status_msg.edit_text(
                message,
                reply_markup=Keyboards.back_to_files(),
                parse_mode='Markdown'
            )
        
        self.sessions.reset_state(user_id)
    
    async def handle_document(self, update: Update, context: ContextTypes.DEFAULT_TYPE):
        """Handle document uploads (files or SSH keys)."""
        user_id = update.effective_user.id
        user_state = self.sessions.get_user_state(user_id)
        document = update.message.document
        
        if user_state.state == "awaiting_key":
            # Handle SSH key upload
            await self._handle_key_upload(update, context, document)
        elif user_state.state == "awaiting_file_upload" or self.ssh.is_connected(user_id):
            # Handle file upload to server
            await self._handle_file_upload(update, context, document)
        else:
            await update.message.reply_text(
                "ℹ️ Send files when connected to upload to SSH server.",
                reply_markup=Keyboards.main_menu(False)
            )
    
    async def _handle_key_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE, document):
        """Handle SSH private key upload."""
        user_id = update.effective_user.id
        
        # Download the key file
        file = await document.get_file()
        key_data = await file.download_as_bytearray()
        
        # Get connection details
        host = self.sessions.get_temp_data(user_id, 'host')
        port = self.sessions.get_temp_data(user_id, 'port', 22)
        username = self.sessions.get_temp_data(user_id, 'username')
        
        # Show connecting message
        status_msg = await update.message.reply_text(
            f"🔄 Connecting to `{host}:{port}` as `{username}` with SSH key...",
            parse_mode='Markdown'
        )
        
        # Attempt connection
        success, message = self.ssh.create_connection(
            user_id=user_id,
            host=host,
            port=port,
            username=username,
            key_data=bytes(key_data)
        )
        
        # Update status message
        await status_msg.edit_text(
            message,
            reply_markup=Keyboards.main_menu(success),
            parse_mode='Markdown'
        )
        
        if success:
            self.sessions.set_state(user_id, 'connected')
        
        # Clear temporary data
        self.sessions.clear_temp_data(user_id)
    
    async def _handle_file_upload(self, update: Update, context: ContextTypes.DEFAULT_TYPE, document):
        """Handle file upload to SSH server."""
        user_id = update.effective_user.id
        
        if not self.ssh.is_connected(user_id):
            await update.message.reply_text(
                "❌ No active SSH connection.",
                reply_markup=Keyboards.main_menu(False)
            )
            return
        
        # Get remote path from temp data or use filename
        remote_path = self.sessions.get_temp_data(user_id, 'upload_path', document.file_name)
        
        # Show uploading message
        status_msg = await update.message.reply_text(
            f"📤 Uploading `{document.file_name}` to `{remote_path}`...",
            parse_mode='Markdown'
        )
        
        # Download file from Telegram
        file = await document.get_file()
        from io import BytesIO
        file_data = BytesIO()
        await file.download_to_memory(file_data)
        file_data.seek(0)
        
        # Upload to SSH server
        success, message = self.ssh.upload_file(user_id, file_data, remote_path)
        
        await status_msg.edit_text(
            message,
            reply_markup=Keyboards.main_menu(True),
            parse_mode='Markdown'
        )
        
        self.sessions.reset_state(user_id)
    
    async def _handle_file_to_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle filename input for editing."""
        user_id = update.effective_user.id
        filepath = text.strip()
        
        if not filepath:
            await update.message.reply_text(
                "❌ Please enter a valid filename.",
                reply_markup=Keyboards.back_to_main()
            )
            return
        
        # Import here to avoid circular import
        from utils import FileEditor
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        # Get file info
        success, file_info, error_msg = FileEditor.get_file_info(self.ssh, user_id, filepath)
        if not success:
            await update.message.reply_text(
                f"❌ {error_msg}",
                reply_markup=Keyboards.file_manager_menu()
            )
            self.sessions.reset_state(user_id)
            return
        
        # Check if it's a text file
        if not FileEditor.is_text_file(self.ssh, user_id, filepath):
            await update.message.reply_text(
                f"⚠️ `{filepath}` is not a text file.\n\n"
                "Only text files can be edited.",
                reply_markup=Keyboards.file_manager_menu(),
                parse_mode='Markdown'
            )
            self.sessions.reset_state(user_id)
            return
        
        # Read file content
        success, content, error_msg = FileEditor.read_file(self.ssh, user_id, filepath)
        if not success:
            await update.message.reply_text(
                f"❌ {error_msg}",
                reply_markup=Keyboards.file_manager_menu()
            )
            self.sessions.reset_state(user_id)
            return
        
        # Store file content for editing
        self.sessions.set_state(user_id, 'editing_file')
        self.sessions.set_temp_data(user_id, 'editing_filepath', filepath)
        self.sessions.set_temp_data(user_id, 'original_content', content)
        
        keyboard = [
            [InlineKeyboardButton("✏️ Send New Content", callback_data=f"edit_content:{filepath}")],
            [InlineKeyboardButton("❌ Cancel", callback_data="file_cancel_edit:0")],
            [InlineKeyboardButton("🔙 Back", callback_data="menu_files")]
        ]
        
        # Show preview
        preview = content[:3000] + "\n... (truncated)" if len(content) > 3000 else content
        
        await update.message.reply_text(
            f"📝 **Editing:** `{filepath}`\n"
            f"📊 **Size:** {FileEditor.format_size(file_info['size'])}\n"
            f"🔒 **Permissions:** {file_info['permissions']}\n\n"
            f"**Current Content:**\n```\n{preview}\n```\n\n"
            "✏️ **Send the new content** as a text message to replace the file.",
            reply_markup=InlineKeyboardMarkup(keyboard),
            parse_mode='Markdown'
        )
    
    async def _handle_file_content_edit(self, update: Update, context: ContextTypes.DEFAULT_TYPE, text: str):
        """Handle new file content from user."""
        user_id = update.effective_user.id
        filepath = self.sessions.get_temp_data(user_id, 'editing_filepath')
        
        if not filepath:
            await update.message.reply_text(
                "❌ No file being edited.",
                reply_markup=Keyboards.file_manager_menu()
            )
            return
        
        # Import here to avoid circular import
        from utils import FileEditor
        from telegram import InlineKeyboardButton, InlineKeyboardMarkup
        
        # Save the new content
        success, message = FileEditor.write_file(self.ssh, user_id, filepath, text)
        
        # Clear editing state
        self.sessions.reset_state(user_id)
        self.sessions.clear_temp_data(user_id)
        
        keyboard = [[InlineKeyboardButton("📂 File Manager", callback_data="menu_files")]]
        
        if success:
            await update.message.reply_text(
                f"{message}\n\n"
                f"📁 **File:** `{filepath}`\n"
                f"💾 **Size:** {FileEditor.format_size(len(text))} bytes\n\n"
                "✅ Changes saved successfully!",
                reply_markup=InlineKeyboardMarkup(keyboard),
                parse_mode='Markdown'
            )
        else:
            await update.message.reply_text(
                f"{message}",
                reply_markup=InlineKeyboardMarkup(keyboard)
            )
