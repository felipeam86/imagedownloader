#!/usr/bin/env python
# -*- coding: utf-8 -*-

"""
CLI for image downloader
"""

import argparse

from . import logger, download
from . import config

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

    parser.add_argument('-o', '--store_path', type=str, default=config.STORE_PATH,
                        help="Root path where images should be stored")

    parser.add_argument('--thumbs', type=int, action='append',
                        help="Thumbnail size to be created. "
                             "Can be specified as many times as thumbs sizes you want")

    parser.add_argument('--n_workers', type=int, default=config.N_WORKERS,
                        help="Number of simultaneous threads to use")

    parser.add_argument('--timeout', type=float, default=config.TIMEOUT,
                        help="Timeout to be given to the url request")

    parser.add_argument('--min_wait', type=float, default=config.MIN_WAIT,
                        help="Minimum wait time between image downloads")

    parser.add_argument('--max_wait', type=float, default=config.MAX_WAIT,
                        help="Maximum wait time between image downloads")

    parser.add_argument('--proxy', type=str, action='append',
                        help="Proxy or list of proxies to use for the requests")

    parser.add_argument('-u', '--user_agent', type=str, default=config.USER_AGENT,
                        help="User agent to be used for the requests")

    parser.add_argument('-f', '--force', action='store_true',
                        help="Force the download even if the files already exists")

    parser.add_argument('--notebook', action='store_true',
                        help="Use the notebook version of tqdm")

    parser.add_argument('-d', '--debug', action='store_true',
                        help="Activate debug mode")

    args = parser.parse_args(args)

    return args


def pprint_args_attributes(args):
    """Print arguments parsed from the CLI
    """
    title = '\033[92mImage downloader called with the following arguments :\033[0m'
    print_args = '\n' + '=' * len(title) + '\n{}\n'.format(title)
    for attr in dir(args):
        if attr[0] != '_':
            print_args += attr.ljust(15) + '--> ' + str(getattr(args, attr)) + '\n'

    return print_args + '=' * len(title)


def update_config_with_args(args):

    config.HEADERS.update({'User-Agent': args.user_agent})

    if args.proxy is not None:
        config.PROXIES = [
            {
                "http": proxy,
                "https": proxy
            }
            for proxy in args.proxy
        ]

    if args.thumbs is not None:
        config.THUMBS = True
        config.THUMBS_SIZES = {
            str(thumb): (thumb, thumb)
            for thumb in args.thumbs
        }

    return config


def main(args=None):
    args = parse(args)

    with open(args.urls, 'r') as fh:
        urls = [url.strip('\n') for url in fh.readlines()]

    config = update_config_with_args(args)

    if args.debug:
        print(pprint_args_attributes(args))
        logger.debug('User-Agent: ' + config.HEADERS['User-Agent'])
        logger.debug('Proxies: ' + str(config.PROXIES))
        logger.debug('Thumbs: ' + str(config.THUMBS_SIZES))


    results = download(
        urls,
        args.store_path,
        thumbs=config.THUMBS,
        thumbs_size=config.THUMBS_SIZES,
        n_workers=args.n_workers,
        timeout=args.timeout,
        min_wait=args.min_wait,
        max_wait=args.max_wait,
        proxies=config.PROXIES,
        headers=config.HEADERS,
        force=args.force,
        notebook=args.notebook,
    )

    downloaded_imgs = len([
        response
        for url, response in results.items()
        if response is not None
    ])

    logger.debug(
        "Downloaded {:0.2%} of images ({})".format(
            downloaded_imgs / len(urls),
            downloaded_imgs
        )
    )
