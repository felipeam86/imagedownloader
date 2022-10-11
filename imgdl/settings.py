import logging
import sys
from multiprocessing import cpu_count
from pathlib import Path

import yaml
from pythonjsonlogger import jsonlogger

PACKAGE_NAME = "imgdl"

config = {
    "STORE_PATH": str(Path("~", ".datasets", "imgdl").expanduser()),
    "N_WORKERS": cpu_count() * 10,
    "TIMEOUT": 5.0,
    "MIN_WAIT": 0.0,
    "MAX_WAIT": 0.0,
}


extra_config_files = [
    Path("~/.wit/config.yaml").expanduser(),  # System wide configurations
    Path(".", "config.yaml"),  # Project specific configurations
]

for config_file in extra_config_files:
    if config_file.exists():
        extra_config = yaml.load(config_file.open())
        if PACKAGE_NAME in extra_config:
            config.update(extra_config[PACKAGE_NAME])


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
