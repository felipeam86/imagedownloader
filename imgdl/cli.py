#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI for image downloader
"""

import argparse
from pathlib import Path

from . import download
from .settings import config

__author__ = "Felipe Aguirre Martinez"
__copyright__ = "Copyright 2017, Workit software"
__email__ = "faguirre@workit-software.com"


def parse(args=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Bulk image downloader from a list of urls"
    )

    parser.add_argument('urls', type=str,
                        help="Text file with the list of urls to be downloaded")

    parser.add_argument('-o', '--store_path', type=str, default=config['STORE_PATH'],
                        help="Root path where images should be stored")

    parser.add_argument('--n_workers', type=int, default=config['N_WORKERS'],
                        help="Number of simultaneous threads to use")

    parser.add_argument('--timeout', type=float, default=config['TIMEOUT'],
                        help="Timeout to be given to the url request")

    parser.add_argument('--min_wait', type=float, default=config['MIN_WAIT'],
                        help="Minimum wait time between image downloads")

    parser.add_argument('--max_wait', type=float, default=config['MAX_WAIT'],
                        help="Maximum wait time between image downloads")

    parser.add_argument('--proxy', type=str, action='append', default=config['PROXIES'],
                        help="Proxy or list of proxies to use for the requests")

    parser.add_argument('-u', '--user_agent', type=str, default=config['USER_AGENT'],
                        help="User agent to be used for the requests")

    parser.add_argument('-f', '--force', action='store_true',
                        help="Force the download even if the files already exists")

    parser.add_argument('--notebook', action='store_true',
                        help="Use the notebook version of tqdm")

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Activate debug mode")

    args = parser.parse_args(args)

    return args


def main(args=None):
    args = parse(args)
    urls = Path(args.urls).read_text().strip().split()
    _ = download(
        urls,
        store_path=args.store_path,
        n_workers=args.n_workers,
        timeout=args.timeout,
        min_wait=args.min_wait,
        max_wait=args.max_wait,
        proxies=args.proxy,
        user_agent=args.user_agent,
        notebook=args.notebook,
        debug=args.debug,
        force=args.force,
    )
