imgdl
=====

Python package for downloading a collection of images from a list of
urls. It comes with the following features:

-  Downloads are multithreaded using ``concurrent.futures``.
-  Relies on a persistent cache. Already downloaded images are not
   downloaded again, unless you force ``imgdl`` to do so.
-  Can hide requests behind proxies
-  It can be used as a command line utility or as a python library.
-  Normalizes images to JPG format + RGB mode after download.
-  Generates thumbnails of varying sizes automatically.
-  Can space downloads with a random timeout drawn from an uniform
   distribution.

Installation
------------

.. code:: bash

    pip install imgdl

Or, from the root project directory:

.. code:: bash

    pip install .

Usage
-----

Here is a simple example using the default configurations:

.. code:: python

    from imgdl import download

    urls = [
        'https://upload.wikimedia.org/wikipedia/commons/9/92/Moh_%283%29.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/8/8b/Moh_%284%29.jpg',
        'https://upload.wikimedia.org/wikipedia/commons/c/cd/Rostige_T%C3%BCr_P4RM1492.jpg'
    ]

    paths = download(urls, store_path='~/.datasets/images', n_workers=50)

``100%|███████████████████████████████████| 3/3 [00:08<00:00,  2.68s/it]``

Images will be downloaded to ``~/.datasets/images`` using 50 threads.
The function returns the list of paths to each image. Paths are
constructed as ``{store_data}/{SHA1-hash(url).jpg}``. If for any reason a
download fails, ``imgdl`` returns a ``None`` as path.

Notice that if you invoke ``download`` again with the same urls, it
will not download them again as it will check first that they are
already downloaded.

.. code:: python

    paths = download(urls, store_path='~/.datasets/images', n_workers=50)

``100%|████████████████████████████████| 3/3 [00:00<00:00, 24576.00it/s]``

Download was instantaneous! and ``imgdl`` is clever enough to return
the image paths.

Here is the complete list of parameters taken by ``download``:

-  ``iterator``: The only mandatory parameter. Usually a list of urls,
   but can be any kind of iterator.
-  ``store_path``: Root path where images should be stored
-  ``n_workers``: Number of simultaneous threads to use
-  ``timeout``: Timeout that the url request should tolerate
-  ``thumbs``: If True, create thumbnails of sizes according to
   thumbs_size
-  ``thumbs_size``: Dictionary of the kind {name: (width, height)}
   indicating the thumbnail sizes to be created.
-  ``min_wait``: Minimum wait time between image downloads
-  ``max_wait``: Maximum wait time between image downloads
-  ``proxies``: Proxy or list of proxies to use for the requests
-  ``headers``: headers to be given to ``requests``
-  ``user_agent``: User agent to be used for the requests
-  ``notebook``: If True, use the notebook version of tqdm progress bar
-  ``debug`` If True, ``imgdl`` logs urls that could not be downloaded
-  ``force``: ``download`` checks first if the image already exists on
   ``store_path`` in order to avoid double downloads. If you want to
   force downloads, set this to True.

Most of these parameters can also be set on a ``config.yaml`` file found
on the directory where the Python process was launched. See
`config.yaml.example`_

Command Line Interface
----------------------

It can also be used as a command line utility:

.. code:: bash

    $ imgdl --help
    usage: imgdl [-h] [-o STORE_PATH] [--thumbs THUMBS] [--n_workers N_WORKERS]
                 [--timeout TIMEOUT] [--min_wait MIN_WAIT] [--max_wait MAX_WAIT]
                 [--proxy PROXY] [-u USER_AGENT] [-f] [--notebook] [-d]
                 urls

    Bulk image downloader from a list of urls

    positional arguments:
      urls                  Text file with the list of urls to be downloaded

    optional arguments:
      -h, --help            show this help message and exit
      -o STORE_PATH, --store_path STORE_PATH
                            Root path where images should be stored (default:
                            ~/.datasets/imgdl)
      --thumbs THUMBS       Thumbnail size to be created. Can be specified as many
                            times as thumbs sizes you want (default: None)
      --n_workers N_WORKERS
                            Number of simultaneous threads to use (default: 50)
      --timeout TIMEOUT     Timeout to be given to the url request (default: 5.0)
      --min_wait MIN_WAIT   Minimum wait time between image downloads (default:
                            0.0)
      --max_wait MAX_WAIT   Maximum wait time between image downloads (default:
                            0.0)
      --proxy PROXY         Proxy or list of proxies to use for the requests
                            (default: None)
      -u USER_AGENT, --user_agent USER_AGENT
                            User agent to be used for the requests (default:
                            Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0)
                            Gecko/20100101 Firefox/55.0)
      -f, --force           Force the download even if the files already exists
                            (default: False)
      --notebook            Use the notebook version of tqdm (default: False)
      -d, --debug           Activate debug mode (default: False)


Download images from google
===========================

This is an example of how we can use ``imgdl`` to download images from a google image search.
I currently use this to quickly build up image datasets. I took inspiration from `this`_ blog
post by `pyimagesearch`_.

Requirements
------------

Install imgdl with the ``[google]`` extra requirements:

.. code:: bash

    pip install "imgdl[google]" 


Download the webdriver for Chrome `here`_  and make sure it’s in your PATH, e. g., place it in /usr/bin or /usr/local/bin.

.. code:: bash

    sudo cp chromedriver /usr/local/bin/

Clone this repository, or simply download the ``google.py`` script.

Usage
-----


You are ready to download images from a google images search. Here is an example of usage:

.. code:: bash

    $ python google.py "paris by night" -n 600 --interactive
    Querying google images for 'paris by night'
    Scrolling down five times
    600 images found.
    Downloading to /Users/aguirre/Projets/imagedownloader/examples/images
    100%|█████████████████████████████| 600/600 [01:15<00:00,  7.91it/s]
    2018-03-04 23:21:52,616 - imgdl.downloader - INFO - 0 images failed to download

The first argument is the query to be sent to google. With ``-n 600`` you are asking for at least 600 images.
By default, a google image query page has only 100 images and requires you to scroll down if you want more.
What the script is doing is using `selenium`_ to simulate a browsing session and scroll down on google search.
With the ``--interactive`` flag, chrome will open and you will be able to see how it scrolls down in order to
get more images. Here is the full list of the command line options:

.. code:: bash

    $ python google.py --help
    usage: google.py [-h] [-n N_IMAGES] [--interactive] [-o STORE_PATH]
                     [--thumbs THUMBS] [--n_workers N_WORKERS] [--timeout TIMEOUT]
                     [--min_wait MIN_WAIT] [--max_wait MAX_WAIT] [--proxy PROXY]
                     [-u USER_AGENT] [-f] [--notebook] [-d]
                     query

    Download images from a google images query

    positional arguments:
      query                 Query string to be executed on google images

    optional arguments:
      -h, --help            show this help message and exit
      -n N_IMAGES, --n_images N_IMAGES
                            Number of expected images to download (default: 100)
      --interactive         Open up chrome interactively to see the search results
                            and scrolling action. (default: False)
      -o STORE_PATH, --store_path STORE_PATH
                            Root path where images should be stored (default:
                            images)
      --thumbs THUMBS       Thumbnail size to be created. Can be specified as many
                            times as thumbs sizes you want (default: None)
      --n_workers N_WORKERS
                            Number of simultaneous threads to use (default: 40)
      --timeout TIMEOUT     Timeout to be given to the url request (default: 5.0)
      --min_wait MIN_WAIT   Minimum wait time between image downloads (default:
                            0.0)
      --max_wait MAX_WAIT   Maximum wait time between image downloads (default:
                            0.0)
      --proxy PROXY         Proxy or list of proxies to use for the requests
                            (default: None)
      -u USER_AGENT, --user_agent USER_AGENT
                            User agent to be used for the requests (default:
                            Mozilla/5.0 (X11; Ubuntu; Linux x86_64; rv:55.0)
                            Gecko/20100101 Firefox/55.0)
      -f, --force           Force the download even if the files already exists
                            (default: False)
      --notebook            Use the notebook version of tqdm (default: False)
      -d, --debug           Activate debug mode (default: False)


Acknowledgements
----------------

Images used for tests are from the `wikimedia commons`_

.. _config.yaml.example: config.yaml.example
.. _wikimedia commons: https://commons.wikimedia.org
.. _here: https://sites.google.com/a/chromium.org/chromedriver/downloads
.. _this: https://www.pyimagesearch.com/2017/12/04/how-to-create-a-deep-learning-dataset-using-google-images/
.. _pyimagesearch: https://www.pyimagesearch.com/
.. _selenium: http://selenium-python.readthedocs.io/
