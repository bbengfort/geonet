# geonet.utils.timer
# Provides timing utilities with human readable results.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 10:56:58 2018 -0500
#
# ID: timer.py [] benjamin@bengfort.com $

"""
Provides timing utilities with human readable results.
"""

##########################################################################
## Imports
##########################################################################

import time

from functools import wraps
from .timez import humanizedelta


##########################################################################
## Decorator
##########################################################################

def timeit(func, wall_clock=True):
    """
    Appends the return with a Timer object recording function execution time.
    """
    @wraps(func)
    def timer_wrapper(*args, **kwargs):
        """
        Inner function that uses the Timer context object
        """
        with Timer(wall_clock) as timer:
            result = func(*args, **kwargs)

        return result, timer
    return timer_wrapper


##########################################################################
## Timer functions
##########################################################################

class Timer(object):
    """
    A context object timer. Usage:
        >>> with Timer() as timer:
        ...     do_something()
        >>> print timer.elapsed
    """

    def __init__(self, wall_clock=True):
        """
        If wall_clock is True then use time.time() to get the number of
        actually elapsed seconds. If wall_clock is False, use time.clock to
        get the process time instead.
        """
        self.wall_clock = wall_clock
        self.time = time.time if wall_clock else time.clock

        # Stubs for serializing an empty timer.
        self.started  = None
        self.finished = None
        self.elapsed  = 0.0

    def __enter__(self):
        self.started  = self.time()
        return self

    def __exit__(self, type, value, tb):
        self.finished = self.time()
        self.elapsed  = self.finished - self.started

    def __str__(self):
        return humanizedelta(seconds=self.elapsed)

    def serialize(self):
        return {
            'started':  self.started,
            'finished': self.finished,
            'elapsed':  humanizedelta(seconds=self.elapsed),
        }
