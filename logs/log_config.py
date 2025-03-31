from loguru import logger
import sys


# Remove the default logger configuration
logger.remove()


# Add a handler for logging to stdout (optional) with AM/PM time format
logger.add(
    sys.stdout, format="{time:DD-MM-YYYY hh:mm:ss A} {level} {message}", level="INFO"
)

# Add a handler for logging to 'app.log' with rotation and AM/PM time format
logger.add(
    "logs/app.log",
    format="{time:DD-MM-YYYY hh:mm:ss A} {level} {message}",
    level="INFO",
    rotation="10 MB",
    compression="zip",
)
