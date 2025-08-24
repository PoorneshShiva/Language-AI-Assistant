import sys

from loguru import logger as loguru_logger

# Remove default handler
loguru_logger.remove()

# Add a new handler that logs to stderr
loguru_logger.add(sys.stderr, level="INFO")

# You can add more handlers here, for example, to log to a file:
loguru_logger.add("file_{time}.log", level="DEBUG", rotation="10 MB")

# Assign the configured logger to 'logging'
logging = loguru_logger

# The logger instance is now configured and can be imported and used elsewhere.
