# geonet.exceptions
# Exception hierarchy for the geonet library.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed Jan 17 07:32:23 2018 -0500
#
# ID: exceptions.py [] benjamin@bengfort.com $

"""
Exception hierarchy for the geonet library.
"""

##########################################################################
## Exception Heirarchy
##########################################################################

class GeoNetException(Exception):
    """
    Base exception for this package
    """
    pass


class ValidationError(GeoNetException):
    """
    Error validating a resource or a collection.
    """
    pass
