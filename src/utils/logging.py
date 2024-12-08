import logging
from pathlib import Path
from rich.logging import RichHandler
from typing import Optional

def setup_logging(output_dir: Path, verbose: bool = False) -> logging.Logger:
    """Setup logging configuration
    
    Args:
        output_dir: Directory for log files
        verbose: Whether to show logs on console
    """
    log_file = output_dir / "transcript_summary.log"
    log_file.parent.mkdir(parents=True, exist_ok=True)
    
    # Create logger
    logger = logging.getLogger("transcript-summarizer")
    logger.setLevel(logging.INFO)
    
    # Clear any existing handlers
    logger.handlers = []
    
    # File handler always writes everything
    file_handler = logging.FileHandler(log_file)
    file_handler.setFormatter(logging.Formatter(
        "%(asctime)s - %(name)s - %(levelname)s - %(message)s"
    ))
    logger.addHandler(file_handler)
    
    # Console handler only if verbose
    if verbose:
        console_handler = RichHandler(rich_tracebacks=True)
        console_handler.setFormatter(logging.Formatter("%(message)s"))
        logger.addHandler(console_handler)
    
    return logger 