"""
SSH Telegram Bot - Main Entry Point

A full-featured Telegram bot for managing SSH connections remotely.
Supports password and key-based authentication, command execution,
file transfers, and session management.
"""
import logging
import asyncio
from telegram import Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    filters
)

from config import Config
from utils import SSHManager, SessionManager, setup_logging
from handlers import CommandHandlers, CallbackHandlers

logger = logging.getLogger(__name__)


class SSHTelegramBot:
    """Main bot class."""
    
    def __init__(self):
        """Initialize the bot."""
        # Validate configuration
        Config.validate()
        
        # Setup logging
        setup_logging(Config.LOG_LEVEL, Config.LOG_FILE, Config.LOG_FORMAT)
        logger.info("Starting SSH Telegram Bot...")
        
        # Initialize managers
        self.ssh_manager = SSHManager()
        self.session_manager = SessionManager()
        
        # Initialize handlers
        self.command_handlers = CommandHandlers(self.ssh_manager, self.session_manager)
        self.callback_handlers = CallbackHandlers(self.ssh_manager, self.session_manager)
        
        # Build application
        self.application = Application.builder().token(Config.BOT_TOKEN).build()
        
        # Register handlers
        self._register_handlers()
        
        logger.info("Bot initialized successfully")
    
    def _register_handlers(self):
        """Register all bot handlers."""
        # Command handlers
        self.application.add_handler(CommandHandler("start", self.command_handlers.start_command))
        self.application.add_handler(CommandHandler("help", self.command_handlers.help_command))
        self.application.add_handler(CommandHandler("connect", self.command_handlers.connect_command))
        self.application.add_handler(CommandHandler("disconnect", self.command_handlers.disconnect_command))
        self.application.add_handler(CommandHandler("status", self.command_handlers.status_command))
        self.application.add_handler(CommandHandler("menu", self.command_handlers.menu_command))
        
        # Callback query handler for inline buttons
        self.application.add_handler(CallbackQueryHandler(self.callback_handlers.handle_callback))
        
        # Document handler for file uploads
        self.application.add_handler(
            MessageHandler(filters.Document.ALL, self.command_handlers.handle_document)
        )
        
        # Message handler for text (must be last)
        self.application.add_handler(
            MessageHandler(filters.TEXT & ~filters.COMMAND, self.command_handlers.handle_message)
        )
        
        # Error handler
        self.application.add_error_handler(self._error_handler)
        
        logger.info("All handlers registered")
    
    async def _error_handler(self, update: Update, context):
        """Handle errors."""
        logger.error(f"Update {update} caused error: {context.error}", exc_info=context.error)
        
        if update and update.effective_message:
            try:
                await update.effective_message.reply_text(
                    "❌ An error occurred. Please try again or use /start to restart."
                )
            except Exception as e:
                logger.error(f"Could not send error message: {e}")
    
    async def _cleanup_sessions(self):
        """Periodic task to cleanup stale SSH sessions."""
        while True:
            try:
                await asyncio.sleep(300)  # Run every 5 minutes
                logger.debug("Running session cleanup...")
                self.ssh_manager.cleanup_stale_sessions()
            except Exception as e:
                logger.error(f"Error in cleanup task: {e}")
    
    def run(self):
        """Run the bot."""
        logger.info("Starting bot polling...")
        
        # Schedule cleanup task to run after bot starts
        async def post_init(app):
            asyncio.create_task(self._cleanup_sessions())
        
        self.application.post_init = post_init
        
        # Run bot
        self.application.run_polling(allowed_updates=Update.ALL_TYPES)


def main():
    """Main entry point."""
    try:
        bot = SSHTelegramBot()
        bot.run()
    except KeyboardInterrupt:
        logger.info("Bot stopped by user")
    except Exception as e:
        logger.error(f"Fatal error: {e}", exc_info=True)
        raise


if __name__ == "__main__":
    main()
