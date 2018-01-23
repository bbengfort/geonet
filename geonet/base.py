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
from collections import MutableMapping, MutableSequence


##########################################################################
## Collection and Resources
##########################################################################

class Resource(MutableMapping):
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

    @property
    def name(self):
        for tag in self.data.get('Tags', []):
            if tag["Key"] == "Name":
                return tag["Value"]
        return None

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

    def serialize(self):
        data = self.data.copy()
        if self.region:
            data["Region"] = str(self.region)
        return data

    def __getitem__(self, key):
        return self.data[key]

    def __setitem__(self, key, val):
        self.data[key] = val

    def __delitem__(self, key):
        del self.data[key]

    def __len__(self):
        return len(self.data)

    def __iter__(self):
        for key in self.data:
            yield key

    def __repr__(self):
        return "<{} in {}>".format(self.__class__.__name__, self.region)

    def __str__(self):
        if self.name: return self.name
        return repr(self)


class Collection(MutableSequence):
    """
    A collection of items loaded from boto responses or JSON on disk and can
    include extra meta data. Collections act half way between a list and a
    dictionary but can be subclassed for specific collection types.
    """

    RESOURCE = Resource

    @classmethod
    def collect(klass, collections, **meta):
        """
        Collect many smaller collections into one big one. Typical usage:

            things = Things.collect(region.things() for region in regions)

        To create a single collection from multiple regions. s
        """
        container = klass([], **meta)
        for collection in collections:
            container += collection
        return container

    def __init__(self, data, region=None, **meta):
        if isinstance(data, dict):
            data = data.values()
        self.region = region
        self.items = [self._make_resource(row) for row in data]
        self.meta = meta

    def _make_resource(self, item):
        if isinstance(item, Resource):
            return item
        return self.RESOURCE(item, self.region)

    def serialize(self):
        return list(self)

    def insert(self, idx, val):
        val = self._make_resource(val)
        return self.items.insert(idx, val)

    def __len__(self):
        return len(self.items)

    def __getitem__(self, idx):
        if isinstance(idx, int):
            return self.items[idx]

        if isinstance(idx, Resource):
            idx = str(idx) 

        if isinstance(idx, basestring):
            for item in self:
                if str(item) == idx:
                    return item

        raise KeyError(
            'no {} with index "{}" found'.format(self.RESOURCE.__name__, idx)
        )

    def __setitem__(self, idx, val):
        self.items[idx] = self._make_resource(val)

    def __delitem__(self, idx):
        del self.items[idx]

    def __repr__(self):
        s = "Collection of {} {}".format(len(self), self.__class__.__name__)
        if self.region:
            s += " in region {}".format(self.region)
        return s
