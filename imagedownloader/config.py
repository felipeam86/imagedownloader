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

# Set where to store downloaded images.
STORE_PATH = 'imgs'

# Create thumbnail versions of the images
THUMBS = False
# Thumbnail sizes to be created
THUMBS_SIZES = {
    'small': (50, 50),
    'big': (200, 200),
}

# Number of threads on which to dispatch the requests.
N_WORKERS = cpu_count()

# Timeout to tolerate while downloading an image
TIMEOUT = 5.0

# Random intentional delay after downloading between MIN_WAIT and MAX_WAIT.
MIN_WAIT = 0.0
MAX_WAIT = 0.0

# Proxy of list of proxies to use for the request.
PROXIES = None

# User agent and headers to use for the request
USER_AGENT = 'Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0) Gecko/20100101 Firefox/55.0'
HEADERS = requests.utils.default_headers()
HEADERS.update(
    {
        'User-Agent': USER_AGENT,
    }
)

# If a config.py file is found on the current working directory,
# override config with it.
custom_config = 'config.py'
if os.path.exists(custom_config):
    logger.debug('Loaded your LOCAL configuration at [{}]'.format(custom_config))
    config_module = sys.modules[__name__]
    override_config = importlib.import_module('config', custom_config)
    for key in dir(override_config):
        if key.isupper():
            setattr(config_module, key, getattr(override_config, key))
