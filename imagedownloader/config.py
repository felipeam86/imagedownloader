#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
The main configuration for image downloader.
All configuration in this file can be overridden by... (to be defined)
"""

from multiprocessing import cpu_count

import requests

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
