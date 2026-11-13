# @generated [partially] Gemini: comments
"""Logging configuration for the application"""
import logging
import sys


def setup_logger() -> logging.Logger:
    """
    Configures and returns a custom logger for the GeoChange app
    Outputs logs both to the console (stdout) and to a local file (app.log)
    """
    # Create a logger
    app_logger = logging.getLogger("geochange")
    app_logger.setLevel(logging.INFO)

    # Define the log format: [Time] LEVEL - Message
    formatter = logging.Formatter(
        fmt="[%(asctime)s] %(levelname)s - %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S"
    )

    # 1. Console
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(formatter)

    # 2. File
    file_handler = logging.FileHandler("app.log", encoding="utf-8")
    file_handler.setFormatter(formatter)

    # prevent duplicates
    if not app_logger.handlers:
        app_logger.addHandler(console_handler)
        app_logger.addHandler(file_handler)

    return app_logger


# Export the configured logger instance
logger = setup_logger()
