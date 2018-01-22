# geonet.utils.async
# Lightweight async library using threading.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 14:24:43 2018 -0500
#
# ID: async.py [] benjamin@bengfort.com $

"""
Lightweight async library using threading.
"""

##########################################################################
## Imports
##########################################################################

from multiprocessing.pool import ThreadPool


MAX_THREADS = 50


##########################################################################
## Asynchronous Helpers
##########################################################################

def wait(funcs, args=(), kwargs={}):
    """
    Execute all functions asynchronously and return all the results as a list.
    """
    pool = ThreadPool(MAX_THREADS)
    results = [
        pool.apply_async(func, args, kwargs)
        for func in funcs
    ]
    pool.close()
    pool.join()
    return [
        result.get() for result in results
    ]
