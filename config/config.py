"""Configuration management for the SSH Telegram Bot."""
import os
from typing import List
from dotenv import load_dotenv

# Load environment variables from .env file
load_dotenv()


class Config:
    """Configuration class for bot settings."""
    
    # Telegram Bot Configuration
    BOT_TOKEN: str = os.getenv('BOT_TOKEN', '')
    
    # Admin Configuration
    ADMIN_IDS: List[int] = [
        int(admin_id.strip()) 
        for admin_id in os.getenv('ADMIN_IDS', '').split(',') 
        if admin_id.strip().isdigit()
    ]
    
    # Logging Configuration
    LOG_LEVEL: str = os.getenv('LOG_LEVEL', 'INFO')
    LOG_FILE: str = os.getenv('LOG_FILE', 'ssh_bot.log')
    LOG_FORMAT: str = '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
    
    # SSH Configuration
    MAX_CONNECTIONS_PER_USER: int = int(os.getenv('MAX_CONNECTIONS_PER_USER', '5'))
    SESSION_TIMEOUT: int = int(os.getenv('SESSION_TIMEOUT', '3600'))  # seconds
    MAX_OUTPUT_LENGTH: int = int(os.getenv('MAX_OUTPUT_LENGTH', '4000'))  # characters
    
    # Connection timeouts
    SSH_CONNECT_TIMEOUT: int = 30  # seconds
    SSH_AUTH_TIMEOUT: int = 30  # seconds
    SSH_BANNER_TIMEOUT: int = 30  # seconds
    
    # File transfer
    MAX_FILE_SIZE: int = 50 * 1024 * 1024  # 50 MB
    CHUNK_SIZE: int = 8192  # bytes
    
    @classmethod
    def validate(cls) -> bool:
        """Validate required configuration."""
        if not cls.BOT_TOKEN:
            raise ValueError("BOT_TOKEN is required. Please set it in .env file.")
        return True
