"""Session persistence to save/restore SSH sessions across bot restarts."""
import json
import logging
from pathlib import Path
from typing import Dict, Optional
from datetime import datetime

logger = logging.getLogger(__name__)


class SessionPersistence:
    """Handle saving and loading of SSH session data."""
    
    def __init__(self, filepath: str = "sessions.json"):
        """
        Initialize session persistence.
        
        Args:
            filepath: Path to session data file
        """
        self.filepath = Path(filepath)
        self.sessions_data: Dict = {}
    
    def save_session(self, user_id: int, session_data: dict):
        """
        Save session data for a user.
        
        Args:
            user_id: Telegram user ID
            session_data: Session information to save
        """
        try:
            # Load existing data
            self.load_sessions()
            
            # Update with new session
            self.sessions_data[str(user_id)] = {
                'host': session_data.get('host'),
                'port': session_data.get('port'),
                'username': session_data.get('username'),
                'password': session_data.get('password'),  # Consider encryption in production
                'current_directory': session_data.get('current_directory', '/'),
                'saved_at': datetime.now().isoformat(),
                'session_id': session_data.get('session_id')
            }
            
            # Save to file
            with open(self.filepath, 'w') as f:
                json.dump(self.sessions_data, f, indent=2)
            
            logger.info(f"Session saved for user {user_id}")
            
        except Exception as e:
            logger.error(f"Error saving session for user {user_id}: {e}")
    
    def load_sessions(self) -> Dict:
        """
        Load all sessions from file.
        
        Returns:
            Dictionary of session data by user ID
        """
        try:
            if self.filepath.exists():
                with open(self.filepath, 'r') as f:
                    self.sessions_data = json.load(f)
                logger.info(f"Loaded {len(self.sessions_data)} sessions from file")
            else:
                self.sessions_data = {}
                logger.info("No existing sessions file found")
            
            return self.sessions_data
            
        except Exception as e:
            logger.error(f"Error loading sessions: {e}")
            return {}
    
    def get_session(self, user_id: int) -> Optional[dict]:
        """
        Get session data for a specific user.
        
        Args:
            user_id: Telegram user ID
            
        Returns:
            Session data dict or None
        """
        self.load_sessions()
        return self.sessions_data.get(str(user_id))
    
    def delete_session(self, user_id: int):
        """
        Delete session data for a user.
        
        Args:
            user_id: Telegram user ID
        """
        try:
            self.load_sessions()
            
            if str(user_id) in self.sessions_data:
                del self.sessions_data[str(user_id)]
                
                # Save updated data
                with open(self.filepath, 'w') as f:
                    json.dump(self.sessions_data, f, indent=2)
                
                logger.info(f"Session deleted for user {user_id}")
        
        except Exception as e:
            logger.error(f"Error deleting session for user {user_id}: {e}")
    
    def clear_all_sessions(self):
        """Clear all saved sessions."""
        try:
            self.sessions_data = {}
            
            if self.filepath.exists():
                self.filepath.unlink()
            
            logger.info("All sessions cleared")
            
        except Exception as e:
            logger.error(f"Error clearing sessions: {e}")
    
    def get_all_user_ids(self) -> list:
        """
        Get list of all user IDs with saved sessions.
        
        Returns:
            List of user IDs
        """
        self.load_sessions()
        return [int(uid) for uid in self.sessions_data.keys()]
