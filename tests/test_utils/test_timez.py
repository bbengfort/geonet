# tests.test_utils.test_timez
# Tests for the timezone handling datetime utilities
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 10:59:38 2018 -0500
#
# ID: test_timez.py [] benjamin@bengfort.com $

"""
Tests for the timezone handling datetime utilities
"""

##########################################################################
## Imports
##########################################################################

import pytz

from geonet.utils.timez import *
from geonet.config import settings


##########################################################################
## Timez Test Cases
##########################################################################


def test_aware_datetimes():
    """
    Assert that localnow and utcnow return tz aware datetimes
    """
    assert localnow().tzinfo is not None, "localnow is tz naive!"
    assert utcnow().tzinfo is not None, "utc is tz naive!"

    assert localnow().strftime(ISO8601_DATETIME)
    assert utcnow().strftime(ISO8601_DATETIME)


def test_humanizedelta():
    """
    Test the humanize delta function to convert seconds
    """
    cases = (
        (12512334, "144 days 19 hours 38 minutes 54 seconds"),
        (34321, "9 hours 32 minutes 1 second"),
        (3428, "57 minutes 8 seconds"),
        (1, "1 second"),
        (0.21, "0 second"),
    )

    for seconds, expected in cases:
        assert humanizedelta(seconds=seconds) == expected


def test_humanizedelta_milliseconds():
    """
    Test the humanize delta function to convert milliseconds
    """

    # Case with seconds already there
    assert humanizedelta(seconds=10, milliseconds=2000) == '12 seconds'

    # Case without seconds present
    assert humanizedelta(milliseconds=456875) == '7 minutes 36 seconds'


def test_resolve_timezone():
    """
    Test timezone resolution with various types
    """
    TZ = pytz.timezone("Australia/Sydney")

    assert resolve_timezone(None) == pytz.timezone(settings.timezone)
    assert resolve_timezone("Australia/Sydney") == TZ
    assert resolve_timezone(TZ) == TZ
