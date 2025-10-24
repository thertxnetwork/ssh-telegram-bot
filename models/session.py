"""SSH session data model."""
from dataclasses import dataclass, field
from datetime import datetime
from typing import Optional


@dataclass
class SSHSession:
    """Represents an SSH session for a user."""
    
    user_id: int
    host: str
    port: int
    username: str
    password: Optional[str] = None
    key_filename: Optional[str] = None
    current_directory: str = "~"
    connected: bool = False
    connected_at: Optional[datetime] = None
    last_activity: Optional[datetime] = None
    session_id: Optional[str] = None
    
    def __post_init__(self):
        """Initialize timestamps."""
        if self.connected and not self.connected_at:
            self.connected_at = datetime.now()
        if not self.last_activity:
            self.last_activity = datetime.now()
    
    def update_activity(self):
        """Update last activity timestamp."""
        self.last_activity = datetime.now()
    
    def to_dict(self) -> dict:
        """Convert session to dictionary."""
        return {
            'user_id': self.user_id,
            'host': self.host,
            'port': self.port,
            'username': self.username,
            'current_directory': self.current_directory,
            'connected': self.connected,
            'connected_at': self.connected_at.isoformat() if self.connected_at else None,
            'last_activity': self.last_activity.isoformat() if self.last_activity else None,
            'session_id': self.session_id,
        }


@dataclass
class UserState:
    """Represents the current state of a user's interaction with the bot."""
    
    user_id: int
    state: str = "idle"  # idle, awaiting_host, awaiting_username, awaiting_password, connected
    temp_data: dict = field(default_factory=dict)
    
    def reset(self):
        """Reset user state to idle."""
        self.state = "idle"
        self.temp_data.clear()
