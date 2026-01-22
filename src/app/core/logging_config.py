"""
Centralized logging configuration for Ambulon applications.
"""

import logging
import sys
import os
from datetime import datetime
from pathlib import Path
from typing import Optional, Union

def setup_logging(level: Union[int, str] = logging.INFO, log_file_prefix: Optional[str] = "ambulon") -> Path:
    """
    Configure the logging system for modules.

    Args:
        level: The logging level (e.g., logging.INFO, "DEBUG").
        log_file_prefix: Prefix for the log file name. If None, only console output.

    Returns:
        Path to the log file if created, None otherwise.
    """
    # Ensure root logger is not configured multiple times
    if logging.root.handlers:
        for handler in logging.root.handlers[:]:
            logging.root.removeHandler(handler)
        logging.root.setLevel(logging.WARNING) # Reset to a higher level to avoid duplicate messages

    now = datetime.now()
    timestamp = now.strftime("%Y-%m-%d_%Hh%Mm%Ss")
    
    log_file: Optional[Path] = None
    logs_dir = None
    # Allow disabling file logs via environment variable
    no_file_logs = os.getenv("AMBULON_NO_FILE_LOGS", "").strip().lower() in {"1", "true", "yes"}

    if log_file_prefix and not no_file_logs:
        try:
            logs_dir = Path("logs")
            logs_dir.mkdir(exist_ok=True)
            log_file = logs_dir / f"{log_file_prefix}.{timestamp}.log"
        except Exception as e:
            # Fallback: disable file logging if we cannot create logs directory
            log_file = None
            try:
                print(f"[WARNING] Logging disabled (cannot create logs/): {e}", file=sys.stderr)
            except Exception:
                pass
    
    # Ensure stdout/stderr encoding for Windows
    import os
    os.environ['PYTHONIOENCODING'] = 'utf-8'
    if hasattr(sys.stdout, 'reconfigure'):
        sys.stdout.reconfigure(encoding='utf-8')
    if hasattr(sys.stderr, 'reconfigure'):
        sys.stderr.reconfigure(encoding='utf-8')
    
    handlers = []
    if log_file:
        file_handler = logging.FileHandler(log_file, encoding='utf-8')
        file_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
        handlers.append(file_handler)
    
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(logging.Formatter("%(asctime)s [%(levelname)s] %(name)s: %(message)s"))
    handlers.append(console_handler)
    
    logging.basicConfig(
        level=level,
        handlers=handlers,
        force=True # Force re-configuration of the root logger
    )
    
    return log_file
