"""Utility functions and helpers."""
import logging
import os
from typing import Optional

logger = logging.getLogger(__name__)


def setup_logging(log_level: str, log_file: Optional[str] = None, log_format: Optional[str] = None):
    """
    Set up logging configuration.
    
    Args:
        log_level: Logging level (DEBUG, INFO, WARNING, ERROR, CRITICAL)
        log_file: Optional log file path
        log_format: Optional log format string
    """
    level = getattr(logging, log_level.upper(), logging.INFO)
    
    handlers = [logging.StreamHandler()]
    if log_file:
        # Create logs directory if it doesn't exist
        log_dir = os.path.dirname(log_file)
        if log_dir and not os.path.exists(log_dir):
            os.makedirs(log_dir)
        handlers.append(logging.FileHandler(log_file))
    
    logging.basicConfig(
        level=level,
        format=log_format or '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=handlers
    )
    
    logger.info(f"Logging initialized at {log_level} level")


def format_output(stdout: str, stderr: str) -> str:
    """
    Format command output for display.
    
    Args:
        stdout: Standard output
        stderr: Standard error
    
    Returns:
        Formatted output string
    """
    output_parts = []
    
    if stdout:
        output_parts.append(f"```\n{stdout}\n```")
    
    if stderr:
        output_parts.append(f"⚠️ **Errors:**\n```\n{stderr}\n```")
    
    if not output_parts:
        return "✅ Command executed successfully (no output)"
    
    return "\n\n".join(output_parts)


def escape_markdown(text: str) -> str:
    """
    Escape special characters for Telegram MarkdownV2.
    
    Args:
        text: Text to escape
    
    Returns:
        Escaped text
    """
    special_chars = ['_', '*', '[', ']', '(', ')', '~', '`', '>', '#', '+', '-', '=', '|', '{', '}', '.', '!']
    for char in special_chars:
        text = text.replace(char, f'\\{char}')
    return text


def validate_host(host: str) -> bool:
    """
    Validate hostname or IP address.
    
    Args:
        host: Hostname or IP address
    
    Returns:
        True if valid, False otherwise
    """
    if not host or len(host) > 255:
        return False
    
    # Basic validation - allow domain names and IPs
    if host.replace('.', '').replace('-', '').replace('_', '').isalnum():
        return True
    
    return False


def validate_port(port: int) -> bool:
    """
    Validate port number.
    
    Args:
        port: Port number
    
    Returns:
        True if valid, False otherwise
    """
    return 1 <= port <= 65535


def get_filename_from_path(path: str) -> str:
    """
    Extract filename from path.
    
    Args:
        path: File path
    
    Returns:
        Filename
    """
    return os.path.basename(path)
