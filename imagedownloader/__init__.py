#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
Bulk image downloader from a list of urls
"""

import logging
import sys

from .downloader import download

__author__ = "Felipe Aguirre Martinez"
__copyright__ = "Copyright 2017, Workit software"
__version__ = 0.1
__email__ = "faguirre@workit-software.com"

__all__ = ['download']

# Create logger
logger = logging.getLogger(__name__)
logger.setLevel(logging.DEBUG)

# Create STDERR handler
handler = logging.StreamHandler(sys.stderr)

# Create formatter and add it to the handler
formatter = logging.Formatter(
    '\033[92m %(asctime)s - %(name)s - %(levelname)s\033[0m - %(message)s')
handler.setFormatter(formatter)

# Set STDERR handler as the only handler
logger.handlers = [handler]
