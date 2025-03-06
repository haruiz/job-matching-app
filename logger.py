import logging
from rich.logging import RichHandler

# Configure logging
logging.basicConfig(
    level=logging.INFO,  # Change to DEBUG for more verbosity
    format="%(message)s",  # RichHandler handles rich formatting
    datefmt="[%X]",
    handlers=[RichHandler(rich_tracebacks=True, markup=True, show_path=False)],
)

# Create logger
logger = logging.getLogger("rich_logger")
