# tests.test_utils.test_timer
# Tests for the timer utility
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 10:58:35 2018 -0500
#
# ID: test_timer.py [] benjamin@bengfort.com $

"""
Tests for the timer utility
"""

##########################################################################
## Imports
##########################################################################

import time

from geonet.utils.timer import *


##########################################################################
## Timer Tests
##########################################################################

def test_timer():
    """
    Test the Timer object with a context manager
    """
    with Timer() as t:
        time.sleep(1)

    assert t.finished > t.started
    assert t.elapsed == t.finished-t.started
    assert str(t) == '1 seconds'

    data = t.serialize()
    for key in ('started', 'finished', 'elapsed'):
        assert key in data

def test_timeit():
    """
    Test the timeit decorator method of timing
    """

    @timeit
    def myfunc():
        return 42

    output = myfunc()
    assert len(output) == 2
    result, timer = output
    assert result == 42
    assert isinstance(timer, Timer)
