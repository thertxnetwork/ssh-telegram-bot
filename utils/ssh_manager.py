"""SSH connection manager with connection pooling and error handling."""
import logging
from typing import Optional, Dict, Tuple
from datetime import datetime, timedelta
import paramiko
from io import BytesIO

from config import Config
from models import SSHSession
from utils.session_persistence import SessionPersistence

logger = logging.getLogger(__name__)


class SSHConnectionError(Exception):
    """Custom exception for SSH connection errors."""
    pass


class SSHManager:
    """Manages SSH connections for users."""
    
    def __init__(self):
        """Initialize SSH manager."""
        self.connections: Dict[int, paramiko.SSHClient] = {}
        self.sessions: Dict[int, SSHSession] = {}
        self.persistence = SessionPersistence()
    
    def create_connection(
        self,
        user_id: int,
        host: str,
        port: int,
        username: str,
        password: Optional[str] = None,
        key_filename: Optional[str] = None,
        key_data: Optional[bytes] = None
    ) -> Tuple[bool, str]:
        """
        Create a new SSH connection.
        
        Args:
            user_id: Telegram user ID
            host: SSH server hostname/IP
            port: SSH server port
            username: SSH username
            password: SSH password (optional)
            key_filename: Path to private key file (optional)
            key_data: Private key data as bytes (optional)
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        try:
            # Check max connections
            if user_id in self.connections:
                self.disconnect(user_id)
            
            # Create SSH client
            client = paramiko.SSHClient()
            client.set_missing_host_key_policy(paramiko.AutoAddPolicy())
            
            # Prepare connection kwargs
            connect_kwargs = {
                'hostname': host,
                'port': port,
                'username': username,
                'timeout': Config.SSH_CONNECT_TIMEOUT,
                'auth_timeout': Config.SSH_AUTH_TIMEOUT,
                'banner_timeout': Config.SSH_BANNER_TIMEOUT,
                'look_for_keys': False,
                'allow_agent': False,
            }
            
            # Add authentication method
            if key_data:
                try:
                    key_file = BytesIO(key_data)
                    pkey = paramiko.RSAKey.from_private_key(key_file)
                    connect_kwargs['pkey'] = pkey
                except Exception as e:
                    logger.error(f"Failed to load private key: {e}")
                    try:
                        key_file = BytesIO(key_data)
                        pkey = paramiko.Ed25519Key.from_private_key(key_file)
                        connect_kwargs['pkey'] = pkey
                    except Exception as e2:
                        logger.error(f"Failed to load Ed25519 key: {e2}")
                        return False, f"Invalid private key format: {str(e)}"
            elif key_filename:
                connect_kwargs['key_filename'] = key_filename
            elif password:
                connect_kwargs['password'] = password
            else:
                return False, "No authentication method provided (password or key required)"
            
            # Connect
            logger.info(f"Attempting SSH connection to {host}:{port} for user {user_id}")
            client.connect(**connect_kwargs)
            
            # Store connection and session
            self.connections[user_id] = client
            session = SSHSession(
                user_id=user_id,
                host=host,
                port=port,
                username=username,
                password=password if password else None,
                key_filename=key_filename if key_filename else None,
                connected=True,
                connected_at=datetime.now(),
                session_id=f"{user_id}_{host}_{datetime.now().timestamp()}"
            )
            self.sessions[user_id] = session
            
            # Save session for persistence (survive restarts)
            self.persistence.save_session(user_id, {
                'host': host,
                'port': port,
                'username': username,
                'password': password,
                'current_directory': session.current_directory,
                'session_id': session.session_id
            })
            
            logger.info(f"SSH connection established for user {user_id}")
            return True, f"✅ Connected to {host}:{port} as {username}"
            
        except paramiko.AuthenticationException as e:
            logger.error(f"Authentication failed for user {user_id}: {e}")
            return False, "❌ Authentication failed. Please check your credentials."
        except paramiko.SSHException as e:
            logger.error(f"SSH error for user {user_id}: {e}")
            return False, f"❌ SSH error: {str(e)}"
        except TimeoutError as e:
            logger.error(f"Connection timeout for user {user_id}: {e}")
            return False, f"❌ Connection timeout. Please check host and port."
        except Exception as e:
            logger.error(f"Unexpected error connecting for user {user_id}: {e}")
            return False, f"❌ Connection error: {str(e)}"
    
    def execute_command(
        self,
        user_id: int,
        command: str,
        timeout: int = 30
    ) -> Tuple[bool, str, str]:
        """
        Execute a command on the SSH connection.
        
        Args:
            user_id: Telegram user ID
            command: Command to execute
            timeout: Command timeout in seconds
        
        Returns:
            Tuple of (success: bool, stdout: str, stderr: str)
        """
        if user_id not in self.connections:
            return False, "", "No active SSH connection. Please connect first."
        
        try:
            client = self.connections[user_id]
            session = self.sessions[user_id]
            
            # Update activity
            session.update_activity()
            
            # Handle cd command specially
            if command.strip().startswith('cd '):
                path = command.strip()[3:].strip()
                # Change directory and update session
                full_cmd = f"cd {session.current_directory} && cd {path} && pwd"
                stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
                
                new_dir = stdout.read().decode('utf-8').strip()
                stderr_output = stderr.read().decode('utf-8').strip()
                
                if stderr_output:
                    return False, "", stderr_output
                
                session.current_directory = new_dir
                
                # Update persisted session
                self.persistence.save_session(user_id, {
                    'host': session.host,
                    'port': session.port,
                    'username': session.username,
                    'password': session.password,
                    'current_directory': session.current_directory,
                    'session_id': session.session_id
                })
                
                return True, f"Changed directory to: {new_dir}", ""
            
            # Execute command in current directory
            full_cmd = f"cd {session.current_directory} && {command}"
            logger.info(f"Executing command for user {user_id}: {command}")
            
            stdin, stdout, stderr = client.exec_command(full_cmd, timeout=timeout)
            
            stdout_output = stdout.read().decode('utf-8', errors='replace')
            stderr_output = stderr.read().decode('utf-8', errors='replace')
            
            # Truncate if too long
            if len(stdout_output) > Config.MAX_OUTPUT_LENGTH:
                stdout_output = stdout_output[:Config.MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
            if len(stderr_output) > Config.MAX_OUTPUT_LENGTH:
                stderr_output = stderr_output[:Config.MAX_OUTPUT_LENGTH] + "\n... (output truncated)"
            
            return True, stdout_output, stderr_output
            
        except paramiko.SSHException as e:
            logger.error(f"SSH error executing command for user {user_id}: {e}")
            return False, "", f"SSH error: {str(e)}"
        except TimeoutError:
            logger.error(f"Command timeout for user {user_id}")
            return False, "", "Command execution timed out"
        except Exception as e:
            logger.error(f"Error executing command for user {user_id}: {e}")
            return False, "", f"Error: {str(e)}"
    
    def upload_file(
        self,
        user_id: int,
        local_file: BytesIO,
        remote_path: str
    ) -> Tuple[bool, str]:
        """
        Upload a file to the SSH server.
        
        Args:
            user_id: Telegram user ID
            local_file: File-like object to upload
            remote_path: Destination path on remote server
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if user_id not in self.connections:
            return False, "No active SSH connection"
        
        try:
            client = self.connections[user_id]
            session = self.sessions[user_id]
            session.update_activity()
            
            sftp = client.open_sftp()
            
            # Handle relative paths
            if not remote_path.startswith('/'):
                remote_path = f"{session.current_directory}/{remote_path}"
            
            sftp.putfo(local_file, remote_path)
            sftp.close()
            
            logger.info(f"File uploaded for user {user_id} to {remote_path}")
            return True, f"✅ File uploaded to {remote_path}"
            
        except Exception as e:
            logger.error(f"Error uploading file for user {user_id}: {e}")
            return False, f"❌ Upload error: {str(e)}"
    
    def download_file(
        self,
        user_id: int,
        remote_path: str
    ) -> Tuple[bool, Optional[BytesIO], str]:
        """
        Download a file from the SSH server.
        
        Args:
            user_id: Telegram user ID
            remote_path: Path to file on remote server
        
        Returns:
            Tuple of (success: bool, file_data: BytesIO, message: str)
        """
        if user_id not in self.connections:
            return False, None, "No active SSH connection"
        
        try:
            client = self.connections[user_id]
            session = self.sessions[user_id]
            session.update_activity()
            
            sftp = client.open_sftp()
            
            # Handle relative paths
            if not remote_path.startswith('/'):
                remote_path = f"{session.current_directory}/{remote_path}"
            
            # Check file size
            file_stat = sftp.stat(remote_path)
            if file_stat.st_size > Config.MAX_FILE_SIZE:
                sftp.close()
                return False, None, f"File too large ({file_stat.st_size} bytes). Max: {Config.MAX_FILE_SIZE} bytes"
            
            # Download file
            file_data = BytesIO()
            sftp.getfo(remote_path, file_data)
            file_data.seek(0)
            sftp.close()
            
            logger.info(f"File downloaded for user {user_id} from {remote_path}")
            return True, file_data, "✅ File downloaded"
            
        except FileNotFoundError:
            return False, None, f"❌ File not found: {remote_path}"
        except Exception as e:
            logger.error(f"Error downloading file for user {user_id}: {e}")
            return False, None, f"❌ Download error: {str(e)}"
    
    def disconnect(self, user_id: int) -> Tuple[bool, str]:
        """
        Disconnect SSH session for a user.
        
        Args:
            user_id: Telegram user ID
        
        Returns:
            Tuple of (success: bool, message: str)
        """
        if user_id not in self.connections:
            return False, "No active connection"
        
        try:
            client = self.connections[user_id]
            client.close()
            
            del self.connections[user_id]
            if user_id in self.sessions:
                del self.sessions[user_id]
            
            # Remove from persistence
            self.persistence.delete_session(user_id)
            
            logger.info(f"SSH connection closed for user {user_id}")
            return True, "✅ Disconnected from SSH server"
            
        except Exception as e:
            logger.error(f"Error disconnecting user {user_id}: {e}")
            return False, f"Error disconnecting: {str(e)}"
    
    def get_session(self, user_id: int) -> Optional[SSHSession]:
        """Get SSH session for a user."""
        return self.sessions.get(user_id)
    
    def is_connected(self, user_id: int) -> bool:
        """Check if user has an active connection."""
        return user_id in self.connections
    
    def cleanup_stale_sessions(self):
        """Clean up sessions that have exceeded timeout."""
        current_time = datetime.now()
        stale_users = []
        
        for user_id, session in self.sessions.items():
            if session.last_activity:
                idle_time = (current_time - session.last_activity).total_seconds()
                if idle_time > Config.SESSION_TIMEOUT:
                    stale_users.append(user_id)
        
        for user_id in stale_users:
            logger.info(f"Cleaning up stale session for user {user_id}")
            self.disconnect(user_id)
    
    def restore_sessions(self):
        """
        Restore saved sessions on bot startup.
        Attempts to reconnect to previously saved SSH sessions.
        """
        saved_sessions = self.persistence.load_sessions()
        
        if not saved_sessions:
            logger.info("No saved sessions to restore")
            return
        
        logger.info(f"Attempting to restore {len(saved_sessions)} saved sessions...")
        
        for user_id_str, session_data in saved_sessions.items():
            try:
                user_id = int(user_id_str)
                
                # Skip if already connected
                if self.is_connected(user_id):
                    continue
                
                # Attempt reconnection
                success, message = self.create_connection(
                    user_id=user_id,
                    host=session_data['host'],
                    port=session_data['port'],
                    username=session_data['username'],
                    password=session_data.get('password')
                )
                
                if success:
                    # Restore directory
                    if 'current_directory' in session_data:
                        session = self.get_session(user_id)
                        if session:
                            session.current_directory = session_data['current_directory']
                    
                    logger.info(f"Restored session for user {user_id}")
                else:
                    logger.warning(f"Failed to restore session for user {user_id}: {message}")
                    # Remove invalid session
                    self.persistence.delete_session(user_id)
                    
            except Exception as e:
                logger.error(f"Error restoring session for user {user_id_str}: {e}")
