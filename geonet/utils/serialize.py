# geonet.utils.serialize
# JSON serialization and encoding utilities for complex objects.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 21:53:58 2018 -0500
#
# ID: serialize.py [] benjamin@bengfort.com $

"""
JSON serialization and encoding utilities for complex objects.
"""

##########################################################################
## Imports
##########################################################################

import pytz
import json

from json import JSONEncoder
from datetime import datetime, date
from geonet.utils.timez import JSON_DATETIME
from geonet.utils.timez import ISO8601_DATETIME, ISO8601_DATE

from functools import partial


##########################################################################
## JSON Encoder
##########################################################################

class Encoder(JSONEncoder):
    """
    Encoder is a series of helpful methods for encoding complex Python
    objects that are not handled by the standard JSONEncoder.
    """

    def default(self, obj):
        """
        Implement this method in a subclass such that it returns
        a serializable object for ``o``, or calls the base implementation
        (to raise a ``TypeError``).
        """
        # If the object has a serialize method, use it.
        if hasattr(obj, 'serialize'):
            return obj.serialize()

        # Handle datetime objects, ensuring they are UTC timestamps
        if isinstance(obj, datetime):
            # Return the UTC encoded timestamp
            if obj.tzinfo is not None:
                obj = obj.astimezone(pytz.utc)
                return obj.strftime(JSON_DATETIME)

            # Return the timestamp with no timezone information
            return obj.strftime(ISO8601_DATETIME)

        # Handle date objects
        if isinstance(obj, date):
            return obj.strftime(ISO8601_DATE)

        # Handle namedtuple objects, converting them to a dictionary
        if hasattr(obj, '_asdict'):
            return obj._asdict()

        # Standard behavior if all else fails
        return super(Encoder, self).default(obj)


##########################################################################
## JSON Dump Helper
##########################################################################

to_json = partial(json.dumps, cls=Encoder)
