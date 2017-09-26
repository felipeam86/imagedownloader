#!/usr/bin/env python
# -*- coding: utf-8 -*-

from codecs import open
from os import path

from setuptools import setup

import imagedownloader

"""
Bulk image downloader from a list of urls
"""

# Get the long description from the README file
here = path.abspath(path.dirname(__file__))
with open(path.join(here, 'README.md'), encoding='utf-8') as f:
    long_description = f.read()

packages = ['imagedownloader']

setup(
    name='imagedownloader',
    version=imagedownloader.__version__,
    description="Bulk image downloader from a list of urls",
    author="Felipe Aguirre Martinez",
    author_email="felipeam86@workit-software.com",
    packages=packages,
    entry_points={'console_scripts': ['imgdownloader=imagedownloader.cli:main']},
    install_requires=[
        'Pillow>=4.2.1',
        'requests>=2.14.2',
        'six>=1.10',
        'tqdm>=4.15.0',
    ],
    extras_require={
        'dev': [
            'jupyter',
            'ipython',
            'Sphinx',
            'pandas'
        ],
    },
    long_description=long_description,
    zip_safe=False
)
