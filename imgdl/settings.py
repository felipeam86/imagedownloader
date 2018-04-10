# -*- coding: utf-8 -*-

from pathlib import Path
from multiprocessing import cpu_count

import yaml
import requests

PACKAGE_NAME = "imgdl"

config = {
    'STORE_PATH': str(Path('~', '.datasets', 'imgdl').expanduser()),
    'THUMBS': False,
    'THUMBS_SIZES': {
        'small': [50, 50],
        'big': [200, 200],
    },
    'N_WORKERS': cpu_count() * 10,
    'TIMEOUT': 5.0,
    'MIN_WAIT': 0.0,
    'MAX_WAIT': 0.0,
    'PROXIES': None,
    'USER_AGENT': 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0',
    'HEADERS': requests.utils.default_headers()
}

config['HEADERS'].update(
    {
        'User-Agent': config['USER_AGENT'],
    }
)

extra_config_files = [
    Path('~/.wit/config.yaml').expanduser(),  # System wide configurations
    Path('.', 'config.yaml')                  # Project specific configurations
]

for config_file in extra_config_files:
    if config_file.exists():
        extra_config = yaml.load(config_file.open())
        if PACKAGE_NAME in extra_config:
            config.update(extra_config[PACKAGE_NAME])
