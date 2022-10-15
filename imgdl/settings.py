import logging
from multiprocessing import cpu_count
from pathlib import Path

from pydantic import BaseSettings
from pythonjsonlogger import jsonlogger


class Base(BaseSettings):
    STORE_PATH: Path = Path("~", ".datasets", "imgdl").expanduser()
    N_WORKERS: int = cpu_count() * 10
    TIMEOUT: float = 5.0
    MIN_WAIT: float = 0.0
    MAX_WAIT: float = 0.0
    LOGFILE: Path = "imgdl.log"


config = Base()


def get_logger(name):

    # Create logger
    logger = logging.getLogger(name)

    # Create formatter and add it to the handler
    formatter = jsonlogger.JsonFormatter(
        "%(asctime) %(name) %(levelname) %(message)",
    )

    # Avoid duplicate handlers
    logger.handlers = []

    filehandler = logging.FileHandler(config.LOGFILE)
    filehandler.setFormatter(formatter)
    filehandler.setLevel(logging.DEBUG)
    logger.addHandler(filehandler)

    # Prevent multiple logging if called from other packages
    logger.propagate = False
    logger.setLevel(logging.DEBUG)

    return logger
