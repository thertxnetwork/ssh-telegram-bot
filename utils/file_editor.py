"""File editor utilities for editing remote files via SSH."""
import logging
from typing import Tuple, Optional, List
from utils.ssh_manager import SSHManager

logger = logging.getLogger(__name__)


class FileEditor:
    """Handle file editing operations using cat and echo commands."""
    
    @staticmethod
    def read_file(ssh_manager: SSHManager, user_id: int, filepath: str) -> Tuple[bool, str, str]:
        """
        Read file contents using cat.
        
        Args:
            ssh_manager: SSH manager instance
            user_id: User ID
            filepath: Path to file
            
        Returns:
            Tuple of (success, content, error_message)
        """
        success, stdout, stderr = ssh_manager.execute_command(
            user_id, 
            f"cat '{filepath}' 2>/dev/null || echo 'FILE_NOT_FOUND'",
            timeout=30
        )
        
        if not success:
            return False, "", stderr
        
        if stdout.strip() == 'FILE_NOT_FOUND':
            return False, "", f"File not found: {filepath}"
        
        # Check if file is too large (max 50KB for editing)
        if len(stdout) > 50000:
            return False, "", "File too large for editing (max 50KB). Use download instead."
        
        return True, stdout, ""
    
    @staticmethod
    def write_file(ssh_manager: SSHManager, user_id: int, filepath: str, content: str) -> Tuple[bool, str]:
        """
        Write content to file using echo and tee.
        
        Args:
            ssh_manager: SSH manager instance
            user_id: User ID
            filepath: Path to file
            content: Content to write
            
        Returns:
            Tuple of (success, message)
        """
        # Escape single quotes in content
        escaped_content = content.replace("'", "'\"'\"'")
        
        # Create backup first
        backup_cmd = f"cp '{filepath}' '{filepath}.backup' 2>/dev/null; echo 'BACKUP_DONE'"
        success, stdout, stderr = ssh_manager.execute_command(user_id, backup_cmd, timeout=10)
        
        # Write new content
        write_cmd = f"printf '%s' '{escaped_content}' > '{filepath}' && echo 'WRITE_SUCCESS' || echo 'WRITE_FAILED'"
        success, stdout, stderr = ssh_manager.execute_command(user_id, write_cmd, timeout=30)
        
        if 'WRITE_SUCCESS' in stdout:
            return True, f"✅ File saved: {filepath}"
        else:
            return False, f"❌ Failed to save file: {stderr}"
    
    @staticmethod
    def get_file_info(ssh_manager: SSHManager, user_id: int, filepath: str) -> Tuple[bool, dict, str]:
        """
        Get file information (size, permissions, type).
        
        Args:
            ssh_manager: SSH manager instance
            user_id: User ID
            filepath: Path to file
            
        Returns:
            Tuple of (success, file_info_dict, error_message)
        """
        cmd = f"stat -c '%s|%A|%U|%G|%y' '{filepath}' 2>/dev/null || echo 'FILE_NOT_FOUND'"
        success, stdout, stderr = ssh_manager.execute_command(user_id, cmd, timeout=10)
        
        if not success or 'FILE_NOT_FOUND' in stdout:
            return False, {}, f"File not found: {filepath}"
        
        parts = stdout.strip().split('|')
        if len(parts) < 5:
            return False, {}, "Failed to get file info"
        
        info = {
            'size': int(parts[0]),
            'permissions': parts[1],
            'owner': parts[2],
            'group': parts[3],
            'modified': parts[4].split('.')[0]
        }
        
        return True, info, ""
    
    @staticmethod
    def format_size(size_bytes: int) -> str:
        """Format bytes to human readable size."""
        for unit in ['B', 'KB', 'MB', 'GB']:
            if size_bytes < 1024.0:
                return f"{size_bytes:.1f} {unit}"
            size_bytes /= 1024.0
        return f"{size_bytes:.1f} TB"
    
    @staticmethod
    def split_content_to_pages(content: str, page_size: int = 3000) -> List[str]:
        """
        Split file content into pages for display.
        
        Args:
            content: File content
            page_size: Characters per page
            
        Returns:
            List of content pages
        """
        if len(content) <= page_size:
            return [content]
        
        pages = []
        lines = content.split('\n')
        current_page = []
        current_size = 0
        
        for line in lines:
            line_size = len(line) + 1  # +1 for newline
            if current_size + line_size > page_size and current_page:
                pages.append('\n'.join(current_page))
                current_page = [line]
                current_size = line_size
            else:
                current_page.append(line)
                current_size += line_size
        
        if current_page:
            pages.append('\n'.join(current_page))
        
        return pages
    
    @staticmethod
    def is_text_file(ssh_manager: SSHManager, user_id: int, filepath: str) -> bool:
        """
        Check if file is a text file using file command.
        
        Args:
            ssh_manager: SSH manager instance
            user_id: User ID
            filepath: Path to file
            
        Returns:
            True if text file, False otherwise
        """
        cmd = f"file -b --mime-type '{filepath}'"
        success, stdout, stderr = ssh_manager.execute_command(user_id, cmd, timeout=5)
        
        if not success:
            return False
        
        mime_type = stdout.strip()
        return mime_type.startswith('text/') or 'json' in mime_type or 'xml' in mime_type
