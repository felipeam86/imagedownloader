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
============

.. code:: bash

    pip install imgdl

Or, from the root project directory:

.. code:: bash

    pip install .

Usage
=====

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
======================

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

Acknowledgements
================

Images used for tests are from the `wikimedia commons`_

.. _config.yaml.example: config.yaml.example
.. _wikimedia commons: https://commons.wikimedia.org
