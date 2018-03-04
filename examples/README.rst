Download images from google
===========================

This is an example of how we can use ``imgdl`` to download images from a google image search.
To run it, first install imgdl as well as some additional requirements:

.. code:: bash

    pip install imgdl selenium beautifulsoup4 lxml


Download the webdriver for Chrome `here`_  and place it in this ``examples/`` folder.
You are ready to download images froma a google images search. Here is an example of usage:

.. code:: bash

    $ python google.py "paris by night" --interactive
    Querying google images for 'paris by night'
    Scrolling down five times
    600 images found.
    Downloading to /Users/aguirre/Projets/imagedownloader/examples/images
    100%|█████████████████████████████| 600/600 [01:15<00:00,  7.91it/s]
    2018-03-04 23:21:52,616 - imgdl.downloader - INFO - 0 images failed to download

And the full command line options:

.. code:: bash

    $ python google.py -h
    usage: google.py [-h] [-f] [--interactive] query

    Download images from a google images query

    positional arguments:
      query          Query string to be executed on google images

    optional arguments:
      -h, --help     show this help message and exit
      -f, --force    Force the download even if the files already exists (default:
                     False)
      --interactive  Open up chrome interactivelly to see the search results and
                     scrolling action. (default: False)

.. _here: https://sites.google.com/a/chromium.org/chromedriver/downloads
