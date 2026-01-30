"""Main entry point for the HOME-AI-AUTOMATION system."""

import logging
import sys
from pathlib import Path

from dotenv import load_dotenv
from flask import Flask

from home_automation.api.routes import create_api_routes
from home_automation.core.automation_engine import AutomationEngine
from home_automation.core.config import Config
from home_automation.core.database import DatabaseManager
from home_automation.core.security import (
    add_security_headers,
    sanitize_log_data,
    setup_rate_limiting,
)


def setup_logging(config: Config) -> None:
    """Set up logging configuration with sanitization."""
    log_level = getattr(logging, config.LOG_LEVEL.upper(), logging.INFO)

    # Ensure logs directory exists
    log_file = Path(config.LOG_FILE)
    log_file.parent.mkdir(parents=True, exist_ok=True)

    # Create custom filter to sanitize logs
    class SanitizingFilter(logging.Filter):
        def filter(self, record):
            if isinstance(record.msg, str):
                record.msg = sanitize_log_data(record.msg)
            return True

    # Create handlers
    file_handler = logging.FileHandler(config.LOG_FILE)
    file_handler.addFilter(SanitizingFilter())

    stream_handler = logging.StreamHandler(sys.stdout)
    stream_handler.addFilter(SanitizingFilter())

    logging.basicConfig(
        level=log_level,
        format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
        handlers=[file_handler, stream_handler]
    )


def create_app() -> Flask:
    """Create and configure the Flask application."""
    # Load environment variables
    load_dotenv()

    # Initialize configuration
    config = Config()

    # Set up logging
    setup_logging(config)
    logger = logging.getLogger(__name__)

    # Create Flask app
    app = Flask(__name__)
    app.config.from_object(config)

    # Add security headers
    add_security_headers(app)

    # Setup rate limiting
    setup_rate_limiting(app)

    # Initialize database
    db_manager = DatabaseManager(config.DATABASE_URL)
    db_manager.initialize()

    # Initialize automation engine
    automation_engine = AutomationEngine(config, db_manager)

    # Set up API routes
    create_api_routes(app, automation_engine)

    # Store references in app context
    app.automation_engine = automation_engine
    app.db_manager = db_manager
    app.config_obj = config

    logger.info("HOME-AI-AUTOMATION application initialized successfully")

    return app


def main():
    """Main entry point."""
    app = create_app()
    config = app.config_obj

    logger = logging.getLogger(__name__)
    logger.info(f"Starting HOME-AI-AUTOMATION server on {config.FLASK_HOST}:{config.FLASK_PORT}")

    try:
        app.run(
            host=config.FLASK_HOST,
            port=config.FLASK_PORT,
            debug=config.FLASK_DEBUG
        )
    except KeyboardInterrupt:
        logger.info("Shutting down HOME-AI-AUTOMATION server...")
        # Cleanup automation engine
        if hasattr(app, 'automation_engine'):
            app.automation_engine.shutdown()
    except Exception as e:
        logger.error(f"Error starting server: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main()
