# geonet.managed
# Maintains a list of instances to manage
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 23:37:34 2018 -0500
#
# ID: managed.py [] benjamin@bengfort.com $

"""
Maintains a list of instances to manage
"""

##########################################################################
## Imports
##########################################################################

import os
import json

from geonet.region import Region
from geonet.config import USERDATA
from geonet.utils.async import wait
from geonet.utils.serialize import Encoder
from geonet.utils.timez import parse_datetime, utcnow

from collections import defaultdict
from functools import partial


INSTANCES  = os.path.join(USERDATA, "instances.json")

##########################################################################
## Managed Instances
##########################################################################

class ManagedInstances(object):
    """
    A mapping of regions to associated instance ids, described by a config.
    """

    @classmethod
    def load(klass, path=INSTANCES):
        """
        Load the managed instances from a path on disk.
        """
        if not os.path.exists(path):
            return klass()

        with open(path, 'r') as f:
            data = json.load(f)
            updated = parse_datetime(data["updated"])
            return klass(data["instances"], updated=updated)

    def __init__(self, data=None, **meta):
        self.meta = meta
        self.data = defaultdict(list)

        if data:
            for region, instances in data.items():
                if isinstance(region, basestring):
                    region = Region({"RegionName": region})
                self.data[region].extend(instances)

    def stop(self, **kwargs):
        """
        Stop all managed instances
        """
        def region_stop(region, instances, **kwds):
            return region.conn.stop_instances(InstanceIds=instances, **kwds)

        reports = wait((
            partial(region_stop, region, instances)
            for region, instances in self.regions()
        ), kwargs=kwargs)

        return [
            status
            for report in reports
            for status in report["StoppingInstances"]
        ]

    def start(self, **kwargs):
        """
        Start all managed instances
        """
        def region_start(region, instances, **kwds):
            return region.conn.start_instances(InstanceIds=instances, **kwds)

        reports = wait((
            partial(region_start, region, instances)
            for region, instances in self.regions()
        ), kwargs=kwargs)

        return [
            status
            for report in reports
            for status in report["StartingInstances"]
        ]

    def regions(self):
        """
        Returns the region and all associated instance ids
        """
        for item in self.data.items():
            yield item

    def serialize(self):
        return {
            "updated": utcnow(),
            "instances": self.data,
        }

    def dump(self, path=INSTANCES):
        """
        Dump the managed instances to the specified path on disk.
        """
        with open(path, 'w') as f:
            json.dump(self, f, cls=Encoder, indent=2)

    def __iter__(self):
        for instances in self.data.values():
            for instance in instances:
                yield instance
