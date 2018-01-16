#!/usr/bin/env python
# setup
# Setuptools script for installing the geonet library and scripts.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 10:16:56 2018 -0500
#
# ID: setup.py [] benjamin@bengfort.com $

"""
Setuptools script for installing the geonet library and scripts.
"""

##########################################################################
## Imports
##########################################################################

import os
import codecs

from setuptools import setup
from setuptools import find_packages

##########################################################################
## Package Information
##########################################################################

## Basic information
NAME         = "geonet"
DESCRIPTION  = "Helper scripts for managing AWS resources around the world."
AUTHOR       = "Benjamin Bengfort"
EMAIL        = "bengfort@cs.umd.edu"
MAINTAINER   = "Benjamin Bengfort"
LICENSE      = "MIT License"
REPOSITORY   = "https://github.com/bbengfort/geonet"
PACKAGE      = "geonet"
SCRIPTS      = ['geonet=geonet.console:main']

## Define the keywords
KEYWORDS     = ('aws', 'distributed systems', 'global', 'replication',)

## Define the classifiers
## See https://pypi.python.org/pypi?%3Aaction=list_classifiers
CLASSIFIERS  = (
    'Development Status :: 3 - Alpha',
    'Environment :: Other Environment',
    'Intended Audience :: Developers',
    'Intended Audience :: Science/Research',
    'License :: OSI Approved :: Apache Software License',
    'Natural Language :: English',
    'Operating System :: OS Independent',
    'Programming Language :: Python',
    'Programming Language :: Python :: 2.7',
    'Topic :: Software Development',
    'Topic :: Software Development :: Libraries :: Python Modules',
)

## Important Paths
PROJECT      = os.path.abspath(os.path.dirname(__file__))
REQUIRE_PATH = "requirements.txt"
TEST_REQUIRE_PATH = "tests/requirements.txt"
VERSION_PATH = os.path.join(PACKAGE, "version.py")
PKG_DESCRIBE = "DESCRIPTION.rst"

## Directories to ignore in find_packages
EXCLUDES     = (
    "tests", "bin", "docs", "fixtures", "register", "notebooks", "conf",
)

##########################################################################
## Helper Functions
##########################################################################

def read(*parts):
    """
    Assume UTF-8 encoding and return the contents of the file located at the
    absolute path from the REPOSITORY joined with *parts.
    """
    with codecs.open(os.path.join(PROJECT, *parts), 'rb', 'utf-8') as f:
        return f.read()


def get_version(path=VERSION_PATH):
    """
    Reads the __init__.py defined in the VERSION_PATH to find the get_version
    function, and executes it to ensure that it is loaded correctly.
    """
    namespace = {}
    exec(read(path), namespace)
    return namespace['get_version'](short=True)


def get_requires(path=REQUIRE_PATH):
    """
    Yields a generator of requirements as defined by the REQUIRE_PATH which
    should point to a requirements.txt output by `pip freeze`.
    """
    for line in read(path).splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            yield line

##########################################################################
## Define the configuration
##########################################################################

config = {
    "name": NAME,
    "version": get_version(),
    "description": DESCRIPTION,
    "long_description": read(PKG_DESCRIBE),
    "license": LICENSE,
    "author": AUTHOR,
    "author_email": EMAIL,
    "maintainer": MAINTAINER,
    "maintainer_email": EMAIL,
    "url": REPOSITORY,
    "download_url": "{}/tarball/v{}".format(REPOSITORY, get_version()),
    "packages": find_packages(where=PROJECT, exclude=EXCLUDES),
    "install_requires": list(get_requires()),
    "setup_requires": ['pytest-runner'],
    "tests_require": list(get_requires(TEST_REQUIRE_PATH)),
    "classifiers": CLASSIFIERS,
    "keywords": KEYWORDS,
    "zip_safe": False,
    "include_package_data": True,
    "entry_points": {
        'console_scripts': SCRIPTS,
    },
}

##########################################################################
## Run setup script
##########################################################################

if __name__ == '__main__':
    setup(**config)
