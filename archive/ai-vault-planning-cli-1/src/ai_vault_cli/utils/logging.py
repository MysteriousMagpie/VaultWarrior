import logging

def setup_logging(log_file='ai_vault_cli.log', level=logging.INFO):
    """Set up logging configuration."""
    logging.basicConfig(
        filename=log_file,
        filemode='a',
        format='%(asctime)s - %(levelname)s - %(message)s',
        level=level
    )

def log_info(message):
    """Log an informational message."""
    logging.info(message)

def log_warning(message):
    """Log a warning message."""
    logging.warning(message)

def log_error(message):
    """Log an error message."""
    logging.error(message)

def log_debug(message):
    """Log a debug message."""
    logging.debug(message)