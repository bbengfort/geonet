# geonet.utils.timez
# Timezone and datetime helper utilities
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 22:01:18 2018 -0500
#
# ID: timez.py [] benjamin@bengfort.com $

"""
Timezone and datetime helper utilities
"""

##########################################################################
## Imports
##########################################################################

import pytz

from datetime import datetime
from dateutil.parser import parse as strptime
from dateutil.relativedelta import relativedelta

from geonet.config import settings


##########################################################################
## Format constants
##########################################################################

HUMAN_DATETIME    = "%a %b %d %H:%M:%S %Y %z"
HUMAN_DATE        = "%b %d, %Y"
HUMAN_TIME        = "%I:%M:%S %p"
HUMAN_HOUR_TZ     = "%-I:%M%p %Z"
JSON_DATETIME     = "%Y-%m-%dT%H:%M:%S.%fZ" # Must be UTC
ISO8601_DATETIME  = "%Y-%m-%dT%H:%M:%S"     # Must be UTC
RFC3339_DATETIME  = "%Y-%m-%d %H:%M:%S%z"
ISO8601_DATE      = "%Y-%m-%d"
ISO8601_TIME      = "%H:%M:%S"


##########################################################################
## Helper Functions
##########################################################################

def utcnow():
    """
    Returns timezone aware UTC timestamp
    """
    now = datetime.utcnow()
    return pytz.utc.localize(now)


def localnow(timezone=None):
    """
    Returns the current timestamp in the specified timezone. If None uses the
    timezone in the configuration file.
    """
    now = utcnow()
    tz  = resolve_timezone(timezone)
    return now.astimezone(tz)


def parse_datetime(dt, timezone=None):
    """
    Parse the given datetime using a variety of format strings, then return
    a datetime aware timezone using the following strategies:

        1. If the timezone is None use timezone in config (default UTC)
        2. If datetime has tzinfo then use astimezone to convert
        3. If datetime has no tzinfo then localize to the given timezone

    Be careful passing timezone naive datetimes into this function!
    """
    timezone = resolve_timezone(timezone)
    timestamp = strptime(dt)

    if timestamp.tzinfo is not None:
        return timestamp.astimezone(timezone)

    return timezone.localize(timestamp)


def resolve_timezone(timezone):
    """
    Converts timezone input into a tzinfo class, returning a default tzinfo if
    None is provided or one cannot be interpreted from the timezone input.
    Timezone can be one of:
        - None:   returns default from settings
        - str:    constructs timezone from tz database string
        - tzinfo: simply returns the tzinfo without exception
    """

    if not timezone:
        return pytz.timezone(settings.timezone)

    if isinstance(timezone, str):
        return pytz.timezone(timezone)

    return timezone


def humanizedelta(*args, **kwargs):
    """
    Wrapper around dateutil.relativedelta (same construtor args) and returns
    a humanized string representing the delta in a meaningful way.
    """
    if 'milliseconds' in kwargs:
        sec  = kwargs.get('seconds', 0)
        msec = kwargs.pop('milliseconds')
        kwargs['seconds'] = sec + (float(msec) / 1000.0)

    delta = relativedelta(*args, **kwargs)
    attrs = ('years', 'months', 'days', 'hours', 'minutes', 'seconds')
    parts = [
        '%d %s' % (getattr(delta, attr), getattr(delta, attr) > 1 and attr or attr[:-1])
        for attr in attrs if getattr(delta, attr)
    ]

    return " ".join(parts)
