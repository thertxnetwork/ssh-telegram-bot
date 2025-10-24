"""Session manager to track user states and SSH sessions."""
import logging
from typing import Dict, Optional
from models import UserState

logger = logging.getLogger(__name__)


class SessionManager:
    """Manages user states and conversation flow."""
    
    def __init__(self):
        """Initialize session manager."""
        self.user_states: Dict[int, UserState] = {}
    
    def get_user_state(self, user_id: int) -> UserState:
        """
        Get or create user state.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            UserState object
        """
        if user_id not in self.user_states:
            self.user_states[user_id] = UserState(user_id=user_id)
        return self.user_states[user_id]
    
    def set_state(self, user_id: int, state: str, **temp_data):
        """
        Set user state and optional temporary data.
        
        Args:
            user_id: Telegram user ID
            state: New state
            **temp_data: Additional temporary data to store
        """
        user_state = self.get_user_state(user_id)
        user_state.state = state
        if temp_data:
            user_state.temp_data.update(temp_data)
        logger.debug(f"User {user_id} state changed to: {state}")
    
    def reset_state(self, user_id: int):
        """
        Reset user state to idle.
        
        Args:
            user_id: Telegram user ID
        """
        if user_id in self.user_states:
            self.user_states[user_id].reset()
            logger.debug(f"User {user_id} state reset to idle")
    
    def get_temp_data(self, user_id: int, key: str, default=None):
        """
        Get temporary data for a user.
        
        Args:
            user_id: Telegram user ID
            key: Data key
            default: Default value if key not found
        
        Returns:
            Stored value or default
        """
        user_state = self.get_user_state(user_id)
        return user_state.temp_data.get(key, default)
    
    def set_temp_data(self, user_id: int, key: str, value):
        """
        Set temporary data for a user.
        
        Args:
            user_id: Telegram user ID
            key: Data key
            value: Value to store
        """
        user_state = self.get_user_state(user_id)
        user_state.temp_data[key] = value
    
    def clear_temp_data(self, user_id: int):
        """
        Clear all temporary data for a user.
        
        Args:
            user_id: Telegram user ID
        """
        user_state = self.get_user_state(user_id)
        user_state.temp_data.clear()
