import logging
import sys
from app.core.config import settings


def setup_logging() -> None:
    """
    Configures structured logging for the application.
    """
    log_level = getattr(logging, settings.LOG_LEVEL.upper(), logging.INFO)

    logging.basicConfig(
        level=log_level,
        format="%(asctime)s | %(levelname)-8s | %(name)s | %(message)s",
        datefmt="%Y-%m-%d %H:%M:%S",
        handlers=[logging.StreamHandler(sys.stdout)],
    )

    # Suppress verbose third-party logs unless DEBUG is explicitly set
    if settings.LOG_LEVEL.upper() != "DEBUG":
        logging.getLogger("uvicorn.access").setLevel(logging.WARNING)
        logging.getLogger("transformers").setLevel(logging.WARNING)
        logging.getLogger("torch").setLevel(logging.WARNING)
        logging.getLogger("PIL").setLevel(logging.WARNING)


logger = logging.getLogger("apextrack")
