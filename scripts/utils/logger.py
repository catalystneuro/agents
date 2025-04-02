import logging
from pathlib import Path


def set_logger(
    name: str = __name__,
    log_to_file: bool = True,
    log_to_stdout: bool = True,
    log_dir: str = "/home/agent_workspace/logs",
    level: int = logging.INFO,
) -> logging.Logger:
    """
    Configure and return a logger with the specified name.

    Args:
        name: Logger name, used for both the logger instance and log filename
        log_to_file: Whether to log to a file
        log_to_stdout: Whether to log to stdout
        log_dir: Directory to store log files
        level: Logging level

    Returns:
        Configured logger instance
    """
    # Create logger
    logger = logging.getLogger(name)
    logger.setLevel(level)

    # Clear any existing handlers
    if logger.hasHandlers():
        logger.handlers.clear()

    # Define formatter
    formatter = logging.Formatter('%(asctime)s - %(levelname)s - %(message)s')

    # Add stdout handler if requested
    if log_to_stdout:
        console_handler = logging.StreamHandler()
        console_handler.setFormatter(formatter)
        logger.addHandler(console_handler)

    # Add file handler if requested
    if log_to_file:
        # Create log directory if it doesn't exist
        log_path = Path(log_dir)
        log_path.mkdir(exist_ok=True, parents=True)

        # Create file handler
        file_handler = logging.FileHandler(
            log_path / f"{name.replace('.', '_')}.log"
        )
        file_handler.setFormatter(formatter)
        logger.addHandler(file_handler)

    return logger
