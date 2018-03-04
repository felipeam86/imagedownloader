#!/usr/bin/env python
# -*- coding: utf-8 -*-

import json
from pathlib import Path
from time import sleep

from imgdl import download
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.keys import Keys

IMAGE_STORE = Path(__file__).parent / 'images'

CHROME_DRIVER = Path(__file__).parent / 'chromedriver'
CHROME_DRIVER_DOWNLOAD_PAGE = "https://sites.google.com/a/chromium.org/chromedriver/downloads"

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


def scroll_down(driver):
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

    # TODO This is not working very well yet... Find a way to know when page finished loading
    # Se this: http://selenium-python.readthedocs.io/waits.html#implicit-waits
    print("Scrolling down five times")
    for i in range(5):
        scroll_down(driver)
        sleep(2)

    urls = get_urls(driver.page_source)

    print(f"{len(urls)} images found.")
    print(f"Downloading to {IMAGE_STORE}")
    paths = download(
        urls,
        store_path=IMAGE_STORE,
        timeout=30,
        debug=True,
        force=args.force
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

    parser.add_argument('-f', '--force', action='store_true',
                        help="Force the download even if the files already exists")

    parser.add_argument('--interactive', action='store_true',
                        help="Open up chrome interactivelly to see the search results and scrolling action.")

    paths = main(parser.parse_args())
