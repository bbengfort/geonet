# geonet.base
# Base classes for handling Amazon resources.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed Jan 17 07:19:39 2018 -0500
#
# ID: base.py [] benjamin@bengfort.com $

"""
Base classes for handling Amazon resources.
"""

##########################################################################
## Imports
##########################################################################

from geonet.exceptions import ValidationError


##########################################################################
## Collection and Resources
##########################################################################

class Resource(object):
    """
    A resource represents an individual item dictionary loaded from boto
    responses or JSON on disk and can include extra meta data. The resource
    can be validated by specifying REQUIRED_KEYS and can be assured to contain
    extra keys by specifying EXTRA_KEYS at the class level.

    Note the string representation of the resource acts as a lookup key in the
    collection, returning the first resource with that string (so they should
    be unique). This is a good way to index resources.
    """

    REQUIRED_KEYS = None
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    def __init__(self, data, region=None):
        self.data = data
        self.region = region
        self.validate()

    def serialize(self):
        data = self.data.copy()
        if self.region:
            data["Region"] = str(self.region)
        return data

    def validate(self):
        for key in self.REQUIRED_KEYS or []:
            if key not in self.data:
                raise ValidationError(
                    'resource {} does not contain required key {}'.format(
                        self.__class__.__name__, key
                    )
                )

        for key in self.EXTRA_KEYS or []:
            if key not in self.data:
                self.data[key] = self.EXTRA_DEFAULT

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def __contains__(self, key):
        return key in self.data

    def __iter__(self):
        for key, val in self.data.items():
            yield key, val

    def __str__(self):
        return str(self.data)


class Collection(object):
    """
    A collection of items loaded from boto responses or JSON on disk and can
    include extra meta data. Collections act half way between a list and a
    dictionary but can be subclassed for specific collection types.
    """

    RESOURCE = Resource

    def __init__(self, data, region=None, **meta):
        if isinstance(data, dict):
            data = data.values()
        self.items = [self.RESOURCE(row, region) for row in data]
        self.meta = meta

    def __len__(self):
        return len(self.items)

    def __iter__(self):
        for item in self.items:
            yield item

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.items[idx]

        if isinstance(idx, basestring):
            for item in self:
                if str(item) == idx:
                    return item

        raise KeyError(
            'no {} with index "{}" found'.format(self.RESOURCE.__name__, idx)
        )

    def __contains__(self, item):
        return item in self.items

    def serialize(self):
        return list(self)
