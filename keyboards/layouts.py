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
                [
                    InlineKeyboardButton("📂 File Manager", callback_data="menu_files"),
                    InlineKeyboardButton("📊 System Monitor", callback_data="menu_monitor")
                ],
                [
                    InlineKeyboardButton("⚡ Quick Commands", callback_data="menu_quick"),
                    InlineKeyboardButton("ℹ️ Session Info", callback_data="menu_info")
                ],
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
        """Create connection options menu."""
        keyboard = [
            [InlineKeyboardButton("🔑 Connect with Password", callback_data="connect_password")],
            [InlineKeyboardButton("🔐 Connect with SSH Key", callback_data="connect_key")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def file_manager_menu() -> InlineKeyboardMarkup:
        """Create file manager main menu."""
        keyboard = [
            [InlineKeyboardButton("📋 Browse Files", callback_data="file_browse")],
            [
                InlineKeyboardButton("📍 Current Dir", callback_data="file_pwd"),
                InlineKeyboardButton("🏠 Home", callback_data="file_home")
            ],
            [
                InlineKeyboardButton("📤 Upload", callback_data="file_upload"),
                InlineKeyboardButton("📥 Download", callback_data="file_download")
            ],
            [
                InlineKeyboardButton("➕ New File", callback_data="file_create"),
                InlineKeyboardButton("📁 New Folder", callback_data="folder_create")
            ],
            [
                InlineKeyboardButton("💾 Disk Usage", callback_data="file_disk_usage"),
                InlineKeyboardButton("🔍 Search", callback_data="file_search")
            ],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def file_browser_menu(page: int = 0, has_prev: bool = False, has_next: bool = False) -> InlineKeyboardMarkup:
        """Create file browser navigation menu."""
        keyboard = []
        
        # Navigation buttons
        nav_row = []
        if has_prev:
            nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"file_page_{page - 1}"))
        nav_row.append(InlineKeyboardButton("🔄 Refresh", callback_data=f"file_page_{page}"))
        if has_next:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"file_page_{page + 1}"))
        keyboard.append(nav_row)
        
        # Action buttons
        keyboard.extend([
            [
                InlineKeyboardButton("📝 Edit File", callback_data="file_edit_select"),
                InlineKeyboardButton("🗑️ Delete", callback_data="file_delete_select")
            ],
            [
                InlineKeyboardButton("✏️ Rename", callback_data="file_rename_select"),
                InlineKeyboardButton("📋 Copy", callback_data="file_copy_select")
            ],
            [
                InlineKeyboardButton("📂 File Manager", callback_data="menu_files"),
                InlineKeyboardButton("« Main Menu", callback_data="menu_main")
            ],
        ])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def file_actions_menu(filepath: str) -> InlineKeyboardMarkup:
        """Create file-specific actions menu."""
        keyboard = [
            [InlineKeyboardButton("📖 View", callback_data=f"file_view:{filepath}")],
            [
                InlineKeyboardButton("📝 Edit", callback_data=f"file_edit:{filepath}"),
                InlineKeyboardButton("📥 Download", callback_data=f"file_dl:{filepath}")
            ],
            [
                InlineKeyboardButton("✏️ Rename", callback_data=f"file_ren:{filepath}"),
                InlineKeyboardButton("📋 Copy", callback_data=f"file_cp:{filepath}")
            ],
            [
                InlineKeyboardButton("🔒 Permissions", callback_data=f"file_chmod:{filepath}"),
                InlineKeyboardButton("ℹ️ Info", callback_data=f"file_info:{filepath}")
            ],
            [InlineKeyboardButton("🗑️ Delete", callback_data=f"file_del:{filepath}")],
            [InlineKeyboardButton("« Back", callback_data="file_browse")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def system_monitor_menu() -> InlineKeyboardMarkup:
        """Create system monitoring menu."""
        keyboard = [
            [
                InlineKeyboardButton("🖥️ System Info", callback_data="mon_system"),
                InlineKeyboardButton("📊 Resources", callback_data="mon_resources")
            ],
            [
                InlineKeyboardButton("⚙️ Top Processes", callback_data="mon_processes"),
                InlineKeyboardButton("💾 Disk Usage", callback_data="mon_disk")
            ],
            [
                InlineKeyboardButton("🌐 Network", callback_data="mon_network"),
                InlineKeyboardButton("🔌 Ports", callback_data="mon_ports")
            ],
            [InlineKeyboardButton("🔄 Refresh All", callback_data="mon_refresh")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def quick_commands_menu() -> InlineKeyboardMarkup:
        """Create quick commands menu."""
        keyboard = [
            [
                InlineKeyboardButton("📋 ls -la", callback_data="quick_ls"),
                InlineKeyboardButton("📍 pwd", callback_data="quick_pwd")
            ],
            [
                InlineKeyboardButton("💾 df -h", callback_data="quick_df"),
                InlineKeyboardButton("🔍 ps aux", callback_data="quick_ps")
            ],
            [
                InlineKeyboardButton("🌐 ifconfig", callback_data="quick_ifconfig"),
                InlineKeyboardButton("🔝 top", callback_data="quick_top")
            ],
            [
                InlineKeyboardButton("📊 free -h", callback_data="quick_free"),
                InlineKeyboardButton("👤 whoami", callback_data="quick_whoami")
            ],
            [
                InlineKeyboardButton("🔄 systemctl", callback_data="quick_systemctl"),
                InlineKeyboardButton("📝 journalctl", callback_data="quick_journal")
            ],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
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
    def session_info_menu() -> InlineKeyboardMarkup:
        """Create session info menu with actions."""
        keyboard = [
            [InlineKeyboardButton("� Refresh Info", callback_data="menu_info")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def help_menu() -> InlineKeyboardMarkup:
        """Create help menu."""
        keyboard = [
            [InlineKeyboardButton("📖 Commands List", callback_data="help_commands")],
            [InlineKeyboardButton("🔐 SSH Key Setup", callback_data="help_ssh_key")],
            [InlineKeyboardButton("� File Manager Guide", callback_data="help_files")],
            [InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def pagination_menu(page: int, total_pages: int, prefix: str = "page") -> InlineKeyboardMarkup:
        """Create pagination menu for large outputs."""
        keyboard = []
        
        nav_row = []
        if page > 0:
            nav_row.append(InlineKeyboardButton("⬅️ Prev", callback_data=f"{prefix}_{page - 1}"))
        
        nav_row.append(InlineKeyboardButton(f"� {page + 1}/{total_pages}", callback_data="noop"))
        
        if page < total_pages - 1:
            nav_row.append(InlineKeyboardButton("➡️ Next", callback_data=f"{prefix}_{page + 1}"))
        
        keyboard.append(nav_row)
        keyboard.append([InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")])
        
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_main() -> InlineKeyboardMarkup:
        """Create simple back button."""
        keyboard = [[InlineKeyboardButton("« Back to Main Menu", callback_data="menu_main")]]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def back_to_files() -> InlineKeyboardMarkup:
        """Create back to file manager button."""
        keyboard = [
            [InlineKeyboardButton("« Back to File Manager", callback_data="menu_files")],
            [InlineKeyboardButton("« Main Menu", callback_data="menu_main")],
        ]
        return InlineKeyboardMarkup(keyboard)
    
    @staticmethod
    def confirm_action(action: str, confirm_data: str, cancel_data: str = "menu_main") -> InlineKeyboardMarkup:
        """Create confirmation keyboard."""
        keyboard = [
            [InlineKeyboardButton(f"✅ Confirm {action}", callback_data=confirm_data)],
            [InlineKeyboardButton("❌ Cancel", callback_data=cancel_data)],
        ]
        return InlineKeyboardMarkup(keyboard)
