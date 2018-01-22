# geonet.region
# Interface for managing region objects
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Wed Jan 17 06:49:35 2018 -0500
#
# ID: region.py [] benjamin@bengfort.com $

"""
Interface for managing region objects
"""

##########################################################################
## Imports
##########################################################################

import os
import json

from geonet.ec2 import connect
from geonet.config import settings
from geonet.config import USERDATA
from geonet.utils.serialize import Encoder
from geonet.base import Collection, Resource
from geonet.utils.timez import utcnow, parse_datetime
from geonet.ec2 import KeyPairs,SecurityGroups
from geonet.ec2 import Instances, Images, LaunchTemplates

from operator import itemgetter


REGIONDATA = os.path.join(USERDATA, "regions.json")


##########################################################################
## Region object and collection
##########################################################################

class Region(Resource):
    """
    A description of a region with extra information stored in config. Expects
    to be initialized from JSON data, an element of a boto response or data
    loaded from disk. This element should be a dictionary only.
    """

    REQUIRED_KEYS = ('Endpoint', 'RegionName')
    EXTRA_KEYS = ('LocaleName')

    @staticmethod
    def from_name(name):
        """
        Load a region from a region name by loading all the region fixtures
        and finding the one that matches the RegionName or LocaleName keys.

        Raises a LookupError if the region could not be found.
        """
        regions = Regions.load()
        region = regions.find(name)
        if region is None:
            raise LookupError("no region named '{}' found".format(name))
        return region

    def __init__(self, *args, **kwargs):
        self._conn = kwargs.pop('conn', None)
        super(Region, self).__init__(*args, **kwargs)

    def __str__(self):
        return self["RegionName"]

    @property
    def locale(self):
        """
        Returns the locale name of the region
        """
        if 'LocaleName' in self and self['LocaleName']:
            return self['LocaleName']

        # Make it up
        parts = self['RegionName'].split('-')
        parts[0] = parts[0].upper()
        parts[1] = parts[1].title()
        return " ".join(parts)

    @property
    def conn(self):
        if self._conn is None:
            self._conn = connect(self)
        return self._conn

    def is_configured(self):
        """
        Returns true if the region is configured in the settings
        """
        return self["RegionName"] in settings.regions

    def instances(self, **kwargs):
        """
        Returns all instances associated with the region
        """
        # TODO: validate response
        resp = self.conn.describe_instances(**kwargs)
        instances = []
        for reservation in resp['Reservations']:
            for instance in reservation['Instances']:
                instance['ReservationId'] = reservation['ReservationId']
                instances.append(instance)
        return Instances(instances, region=self)

    def key_pairs(self, **kwargs):
        """
        Returns the keys associated with the region.
        """
        # TODO: validate response
        resp = self.conn.describe_key_pairs(**kwargs)
        return KeyPairs(resp['KeyPairs'], region=self)

    def launch_templates(self, **kwargs):
        """
        Returns the launch templates associated with the region.
        """
        # TODO: validate response
        resp = self.conn.describe_launch_templates(**kwargs)
        return LaunchTemplates(resp['LaunchTemplates'], region=self)

    def images(self, **kwargs):
        """
        Returns the images associated with the region. By default this filters
        the images that belong to the owner id set in the configuration file,
        otherwise this will take a really long time and return many results.
        """
        if 'Filters' not in kwargs and settings.aws.aws_owner_id:
            kwargs['Filters'] = [{
                'Name': 'owner-id',
                'Values': [settings.aws.aws_owner_id]
            }]

        # TODO: validate response
        resp = self.conn.describe_images(**kwargs)
        return Images(resp['Images'], region=self)

    def security_groups(self, **kwargs):
        """
        Returns the security groups associated with the region.
        """
        # TODO: validate repsonse
        resp = self.conn.describe_security_groups(**kwargs)
        return SecurityGroups(resp['SecurityGroups'], region=self)


class Regions(Collection):
    """
    A collection of region objects with extra information stored in config.
    Expects to be initialized from JSON data, either a response from boto
    describe_regions or loading the data from disk in a saved location.
    """

    RESOURCE = Region

    @classmethod
    def load(klass, path=REGIONDATA):
        """
        Load the region data from a path on disk.
        """

        # Return list of configured regions
        if not os.path.exists(path):
            return klass([
                {'RegionName': region} for region in settings.regions
            ])

        with open(path, 'r') as f:
            data = json.load(f)
            updated = parse_datetime(data["updated"])
            return klass(data["regions"], updated=updated)

    @classmethod
    def fetch(klass, conn):
        """
        Fetch the region data from EC2 with the given connection
        """
        # TODO: validate response
        resp = conn.describe_regions()
        return klass(resp["Regions"])

    def dump(self, path=REGIONDATA):
        """
        Dump the regions to the specified path on disk
        """
        data = {
            "updated": utcnow(),
            "regions": list(self),
        }

        with open(path, 'w') as f:
            json.dump(data, f, cls=Encoder, indent=2)

    def sortby(self, key, reverse=False):
        """
        Sort the region by the specified key
        """
        self.items.sort(key=itemgetter(key), reverse=reverse)

    def find(self, name):
        """
        Find a region by RegionName or by LocaleName. Returns None if no key
        with the specified name could be found. Is case sensitive.
        """
        for region in self:
            if name == region["RegionName"] or name == region.locale:
                return region
        return None


if __name__ == '__main__':
    from geonet.utils.serialize import to_json

    regions = Regions.load()
    region  = regions[settings.aws.aws_region]

    # print(to_json(region.key_pairs(), indent=2))
    print(to_json(region.instances(), indent=2))
    # print(to_json(region.images(), indent=2))
    # print(to_json(region.security_groups(), indent=2))
