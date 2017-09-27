#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The main configuration for image downloader. All configuration in this file
can be overridden by a config.py file living on your current working directory.
"""

import logging
import os
import sys
import importlib
from multiprocessing import cpu_count

import requests

logger = logging.getLogger(__name__)

USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'

HEADERS = requests.utils.default_headers()
HEADERS.update(
    {
        'User-Agent': USER_AGENT,
    }
)

PROXIES = None

N_WORKERS = cpu_count()

THUMBS = False
THUMBS_SIZES = {
    'small': (50, 50),
    'big': (200, 200),
}

custom_config = 'config.py'
if os.path.exists(custom_config):
    logger.debug('Loaded your LOCAL configuration at [{}]'.format(custom_config))
    config_module = sys.modules[__name__]
    override_config = importlib.import_module('config', custom_config)
    for key in dir(override_config):
        if key.isupper():
            setattr(config_module, key, getattr(override_config, key))
