"""Advanced file manager for SSH operations."""
import logging
import os
from typing import Optional, List, Tuple, Dict
from datetime import datetime

logger = logging.getLogger(__name__)


class FileManager:
    """Advanced file management operations."""
    
    @staticmethod
    def parse_ls_output(output: str) -> List[Dict]:
        """Parse ls -la output into structured data."""
        lines = output.strip().split('\n')
        files = []
        
        for line in lines[1:]:  # Skip first line (total)
            if not line.strip():
                continue
            
            parts = line.split()
            if len(parts) < 9:
                continue
            
            permissions = parts[0]
            is_dir = permissions.startswith('d')
            is_link = permissions.startswith('l')
            name = ' '.join(parts[8:])
            
            # Skip . and ..
            if name in ['.', '..']:
                continue
            
            files.append({
                'name': name,
                'permissions': permissions,
                'size': parts[4] if not is_dir else '-',
                'modified': ' '.join(parts[5:8]),
                'is_dir': is_dir,
                'is_link': is_link,
                'icon': '📁' if is_dir else ('🔗' if is_link else FileManager.get_file_icon(name))
            })
        
        return files
    
    @staticmethod
    def get_file_icon(filename: str) -> str:
        """Get emoji icon for file type."""
        ext = os.path.splitext(filename)[1].lower()
        
        icon_map = {
            '.py': '🐍',
            '.js': '📜',
            '.html': '🌐',
            '.css': '🎨',
            '.json': '📋',
            '.xml': '📋',
            '.txt': '📄',
            '.md': '📝',
            '.pdf': '📕',
            '.doc': '📘',
            '.docx': '📘',
            '.xls': '📗',
            '.xlsx': '📗',
            '.zip': '📦',
            '.tar': '📦',
            '.gz': '📦',
            '.jpg': '🖼️',
            '.jpeg': '🖼️',
            '.png': '🖼️',
            '.gif': '🖼️',
            '.mp4': '🎬',
            '.mp3': '🎵',
            '.wav': '🎵',
            '.sh': '⚙️',
            '.conf': '⚙️',
            '.cfg': '⚙️',
            '.log': '📊',
        }
        
        return icon_map.get(ext, '📄')
    
    @staticmethod
    def format_size(size_str: str) -> str:
        """Format file size for better readability."""
        if size_str == '-':
            return '-'
        
        try:
            size = int(size_str)
            for unit in ['B', 'KB', 'MB', 'GB', 'TB']:
                if size < 1024.0:
                    return f"{size:.1f}{unit}"
                size /= 1024.0
            return f"{size:.1f}PB"
        except:
            return size_str
    
    @staticmethod
    def create_file_list_message(files: List[Dict], current_dir: str, page: int = 0, page_size: int = 10) -> Tuple[str, bool, bool]:
        """
        Create formatted file list message with pagination.
        
        Returns:
            Tuple of (message, has_prev, has_next)
        """
        total = len(files)
        start = page * page_size
        end = start + page_size
        page_files = files[start:end]
        
        message = f"📂 **Current Directory:**\n`{current_dir}`\n\n"
        message += f"📊 **Items:** {total} ({start + 1}-{min(end, total)})\n\n"
        
        # Sort: directories first, then files
        dirs = [f for f in page_files if f['is_dir']]
        files_only = [f for f in page_files if not f['is_dir']]
        
        for item in dirs + files_only:
            size = FileManager.format_size(item['size'])
            message += f"{item['icon']} `{item['name']}`\n"
            message += f"   _{item['permissions']}_ | {size} | {item['modified']}\n\n"
        
        has_prev = page > 0
        has_next = end < total
        
        return message, has_prev, has_next
    
    @staticmethod
    def split_output_pages(output: str, page_size: int = 3500) -> List[str]:
        """Split large output into pages."""
        if len(output) <= page_size:
            return [output]
        
        pages = []
        lines = output.split('\n')
        current_page = ""
        
        for line in lines:
            if len(current_page) + len(line) + 1 > page_size:
                pages.append(current_page)
                current_page = line + '\n'
            else:
                current_page += line + '\n'
        
        if current_page:
            pages.append(current_page)
        
        return pages
    
    @staticmethod
    def get_file_info_message(ssh_manager, user_id: int, filepath: str) -> str:
        """Get detailed file information."""
        success, stdout, stderr = ssh_manager.execute_command(
            user_id,
            f"stat '{filepath}' 2>/dev/null || ls -lh '{filepath}'"
        )
        
        if not success or stderr:
            return f"❌ Could not get file info: {stderr}"
        
        return f"📄 **File Information:**\n```\n{stdout}\n```"
