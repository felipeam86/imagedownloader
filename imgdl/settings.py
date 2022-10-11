import logging
import sys
from multiprocessing import cpu_count
from pathlib import Path

from pythonjsonlogger import jsonlogger

from pydantic import BaseSettings

class Base(BaseSettings):
    STORE_PATH: Path = Path("~", ".datasets", "imgdl").expanduser()
    N_WORKERS: int = cpu_count() * 10
    TIMEOUT: float = 5.0
    MIN_WAIT: float = 0.0
    MAX_WAIT: float = 0.0
    LOGFILE: Path = "imgdl.log"

config = Base()


def get_logger(name, filename=None, streamhandler=False):

    # Create logger
    logger = logging.getLogger(name)

    # Create formatter and add it to the handler
    formatter = jsonlogger.JsonFormatter(
        "%(asctime) %(name) %(levelname) %(message)",
    )

    # Avoid duplicate handlers
    logger.handlers = []

    if streamhandler:
        # Create STDERR handler
        handler = logging.StreamHandler(sys.stderr)
        handler.setFormatter(formatter)
        handler.setLevel(logging.WARNING)
        logger.addHandler(handler)

    if filename is not None:
        # Create json formatter
        filehandler = logging.FileHandler(filename)
        filehandler.setFormatter(formatter)
        filehandler.setLevel(logging.DEBUG)
        logger.addHandler(filehandler)

    # Prevent multiple logging if called from other packages
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    return logger
