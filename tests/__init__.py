# tests
# Tests for the geonet library and helpers.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 10:13:51 2018 -0500
#
# ID: __init__.py [] benjamin@bengfort.com $

"""
Tests for the geonet library and helpers.
"""

##########################################################################
## Imports
##########################################################################

import pytest

# Tests match the geonet version
EXPECTED_VERSION = "0.1"

##########################################################################
## Initialization Tests
##########################################################################

class TestInitialization(object):
    """
    Preliminary tests to ensure testing is setup correctly
    """

    def test_sanity(self):
        """
        Ensure the test runner is hooked up correctly
        """
        assert 2+2 == 4

    def test_import(self):
        """
        Ensure we can import the geonet library
        """
        try:
            import geonet
        except ImportError:
            pytest.fail("could not import the geonet library")

    def test_version(self):
        """
        Ensure test version matches mantle version
        """
        import geonet
        assert geonet.__version__ == EXPECTED_VERSION
