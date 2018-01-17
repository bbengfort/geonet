# tests.test_utils.test_serialize
# Tests for the serialization helper methods
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 21:58:25 2018 -0500
#
# ID: test_serialize.py [] benjamin@bengfort.com $

"""
Tests for the serialization helper methods
"""

##########################################################################
## Imports
##########################################################################

import pytz
import json

from datetime import datetime, date
from geonet.utils.serialize import *


##########################################################################
## Test Cases
##########################################################################

class Fixture(object):

    def __init__(self, **kwargs):
        self.vals = kwargs

    def serialize(self):
        return self.vals


class TestSerializers(object):
    """
    Serialization and encoding tests
    """

    def test_json_encoder(self):
        """
        test the mantle custom json encoder class
        """
        expected = json.dumps({
            "fixture": {"color": "red", "meaning": 42},
            "datetime": "2017-07-07T12:38:42.013244Z",
            "date": "2017-07-01",
        })

        values = {
            "fixture": Fixture(color="red", meaning=42),
            "datetime": datetime(2017, 7, 7, 7, 42, 42, 13244, tzinfo=pytz.timezone("America/New_York")),
            "date": date(2017, 7, 1),
        }

        assert json.dumps(values, cls=Encoder) == expected
