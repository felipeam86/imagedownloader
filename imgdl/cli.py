import argparse
from pathlib import Path

from . import download
from .settings import config


def parse(args=None):
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Bulk image downloader from a list of urls",
    )

    parser.add_argument(
        "urls", type=str, help="Text file with the list of urls to be downloaded"
    )

    parser.add_argument(
        "-o",
        "--store_path",
        type=str,
        default=config.STORE_PATH,
        help="Root path where images should be stored",
    )

    parser.add_argument(
        "--n_workers",
        type=int,
        default=config.N_WORKERS,
        help="Number of simultaneous threads to use",
    )

    parser.add_argument(
        "--timeout",
        type=float,
        default=config.TIMEOUT,
        help="Timeout to be given to the url request",
    )

    parser.add_argument(
        "--min_wait",
        type=float,
        default=config.MIN_WAIT,
        help="Minimum wait time between image downloads",
    )

    parser.add_argument(
        "--max_wait",
        type=float,
        default=config.MAX_WAIT,
        help="Maximum wait time between image downloads",
    )

    parser.add_argument(
        "-f",
        "--force",
        action="store_true",
        help="Force the download even if the files already exists",
    )

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
        force=args.force,
    )
