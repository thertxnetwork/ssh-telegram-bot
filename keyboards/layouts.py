"""Inline keyboard layouts for the bot."""
from telegram import InlineKeyboardButton, InlineKeyboardMarkup


class Keyboards:
    """Collection of inline keyboard layouts."""
    
    @staticmethod
    def main_menu(is_connected: bool = False) -> InlineKeyboardMarkup:
        """
        Create main menu keyboard.
        
        Args:
            is_connected: Whether user has an active SSH connection
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = []
        
        if is_connected:
            keyboard.extend([
                [InlineKeyboardButton("📝 Execute Command", callback_data="menu_execute")],
                [InlineKeyboardButton("📂 File Manager", callback_data="menu_files")],
                [InlineKeyboardButton("ℹ️ Session Info", callback_data="menu_info")],
                [InlineKeyboardButton("🔌 Disconnect", callback_data="action_disconnect")],
            ])
        else:
            keyboard.extend([
                [InlineKeyboardButton("🔐 New Connection", callback_data="menu_connect")],
                [InlineKeyboardButton("❓ Help", callback_data="menu_help")],
            ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def connection_menu() -> InlineKeyboardMarkup:
        """
        Create connection options menu.
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = [
            [InlineKeyboardButton("🔑 Connect with Password", callback_data="connect_password")],
            [InlineKeyboardButton("🔐 Connect with SSH Key", callback_data="connect_key")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def file_manager_menu() -> InlineKeyboardMarkup:
        """
        Create file manager menu.
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = [
            [InlineKeyboardButton("📋 List Files (ls)", callback_data="file_list")],
            [InlineKeyboardButton("📍 Current Directory (pwd)", callback_data="file_pwd")],
            [InlineKeyboardButton("📤 Upload File", callback_data="file_upload")],
            [InlineKeyboardButton("📥 Download File", callback_data="file_download")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def session_info_menu() -> InlineKeyboardMarkup:
        """
        Create session info menu with actions.
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = [
            [InlineKeyboardButton("🔄 Refresh Info", callback_data="menu_info")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """
        Create help menu.
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = [
            [InlineKeyboardButton("📖 Commands List", callback_data="help_commands")],
            [InlineKeyboardButton("🔐 SSH Key Setup", callback_data="help_ssh_key")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """
        Create simple back button.
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_files() -> InlineKeyboardMarkup:
        """
        Create back to file manager button.
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = [
            [InlineKeyboardButton("« Back to File Manager", callback_data="menu_files")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str, confirm_data: str, cancel_data: str = "menu_main") -> InlineKeyboardMarkup:
        """
        Create confirmation keyboard.
        
        Args:
            action: Action description
            confirm_data: Callback data for confirm button
            cancel_data: Callback data for cancel button
        
        Returns:
            InlineKeyboardMarkup
        """
        keyboard = [
            [InlineKeyboardButton(f"✅ Confirm {action}", callback_data=confirm_data)],
            [InlineKeyboardButton("❌ Cancel", callback_data=cancel_data)],
        ]
        return InlineKeyboardMarkup(keyboard)
