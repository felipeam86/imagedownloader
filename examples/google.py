#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from time import sleep

from imgdl import download
from imgdl.settings import config
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

IMAGE_STORE = Path(__file__).parent / 'images'

CHROME_DRIVER = Path(__file__).parent / 'chromedriver'
CHROME_DRIVER_DOWNLOAD_PAGE = "https://sites.google.com/a/chromium.org/chromedriver/downloads"
MAX_RETRIES = 3

if not CHROME_DRIVER.exists():
    raise FileNotFoundError(f"'chromedriver' executable not found. "
                            f"Download it from {CHROME_DRIVER_DOWNLOAD_PAGE} "
                            f"and place it next to this script file")


def get_driver(headless=True):
    options = webdriver.ChromeOptions()

    if headless:
        options.add_argument("headless")

    driver = webdriver.Chrome(
        executable_path=str(CHROME_DRIVER),
        options=options
    )

    return driver


def scroll_down(driver, click_more_results=False):
    if click_more_results:
        smr = driver.find_element_by_id("smb")
        if smr.is_displayed():
            smr.click()
    else:
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")


def get_urls(page_source):

    soup = BeautifulSoup(page_source, "lxml")
    return [
        json.loads(rg_di.find("div", class_="rg_meta").contents[0])["ou"]
        for rg_di in soup.find_all("div", class_='rg_di')
    ]


def main(args):

    print(f"Querying google images for '{args.query}'")
    driver = get_driver(headless=not args.interactive)
    driver.get("https://images.google.com")

    elem = driver.find_element_by_name("q")
    elem.send_keys(args.query)
    elem.send_keys(Keys.RETURN)

    urls = get_urls(driver.page_source)
    previous_n = new_n = len(urls)

    current_retries = 0
    n_scrolls = 0
    # Scroll down until there are enough images or unsuccessful retries exceeded maximum retries
    while (new_n < args.n_images) and (current_retries < MAX_RETRIES):
        scroll_down(
            driver,
            click_more_results=(new_n == previous_n) and (current_retries != 0)
        )
        n_scrolls += 1
        print(f"Scrolled {n_scrolls} times already")
        current_retries += 1
        # Do incremental waits until more images appear
        for i in range(4):
            sleep(0.5 * i + 1)
            urls = get_urls(driver.page_source)
            new_n = len(urls)
            if new_n > previous_n:
                current_retries = 0
                print(f"{new_n} images so far")
                break
        previous_n = new_n

    print(f"{len(urls)} images found.")
    store_path = args.store_path / 'google' / args.query.replace(" ", "_")
    print(f"Downloading to {store_path}")
    paths = download(
        urls,
        store_path=store_path,
        n_workers=args.n_workers,
        timeout=args.timeout,
        thumbs=args.thumbs is not None,
        thumbs_size=args.thumbs,
        min_wait=args.min_wait,
        max_wait=args.max_wait,
        proxies=args.proxy,
        user_agent=args.user_agent,
        notebook=args.notebook,
        debug=args.debug,
        force=args.force,
    )

    return dict(zip(urls, paths))


if __name__ == '__main__':

    import argparse
    parser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter,
        description="Download images from a google images query"
    )

    parser.add_argument('query', type=str,
                        help="Query string to be executed on google images")

    parser.add_argument('-n', '--n_images', type=int, default=100,
                        help="Number of expected images to download")

    parser.add_argument('--interactive', action='store_true',
                        help="Open up chrome interactively to see the search results and scrolling action.")

    parser.add_argument('-o', '--store_path', type=str, default=IMAGE_STORE,
                        help="Root path where images should be stored")

    parser.add_argument('--thumbs', type=int, action='append',
                        help="Thumbnail size to be created. "
                             "Can be specified as many times as thumbs sizes you want")

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

    paths = main(parser.parse_args())
