# -*- coding: utf-8 -*-
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

from geonet.config import USERDATA
from geonet.utils.async import wait
from geonet.region import parse_region
from geonet.ec2 import Instance, Instances
from geonet.utils.serialize import Encoder
from geonet.base import Resource, Collection
from geonet.utils.timez import parse_datetime, utcnow

from commis import color
from collections import Set
from functools import partial
from collections import defaultdict


INSTANCES  = os.path.join(USERDATA, "instances.json")

##########################################################################
## Managed Instances
##########################################################################

class ManagedInstances(Set):
    """
    A set of instance ids that are under management by geonet. Underneath the
    datastructure is a mapping of regions to instances so that actions can be
    applied to the managed instances, like stopping, starting, or terminating
    them. Instances can be added or removed from management.

    This class is intended to sit on top of a file on disk, so that the
    management state of the app is stored locally.

    Parameters
    ----------
    data : dict
        A mapping of region to a list of instance ids (must be unique)

    meta : dict
        Any additional information stored with the managed instances.
    """

    @classmethod
    def load(klass, path=INSTANCES):
        """
        Load the managed instances from a path on disk.
        """
        if not os.path.exists(path):
            # Return empty set
            return klass()

        with open(path, 'r') as f:
            data = json.load(f)
            updated = parse_datetime(data["updated"])
            return klass(data["instances"], updated=updated)

    def __init__(self, data=None, **meta):
        self.meta = meta
        self.data = defaultdict(set)

        data = data or {}
        for region, instances in data.items():
            if not instances: continue
            self.data[parse_region(region)] = set(instances)

    def status(self, **kwargs):
        """
        Returns a collection of current instance information
        """
        def region_status(region, instances, **kwds):
            kwds.update({
                "InstanceIds": instances
            })
            return region.instances(**kwds)

        return Instances.collect(wait(
            partial(region_status, region, instances)
            for region, instances in self.regions()
        ), kwargs=kwargs)

    def stop(self, **kwargs):
        """
        Stop all managed instances
        """
        def region_stop(region, instances, **kwds):
            resp = region.conn.stop_instances(InstanceIds=instances, **kwds)
            return StateChanges(resp['StoppingInstances'], region=region)

        return StateChanges.collect(wait((
            partial(region_stop, region, instances)
            for region, instances in self.regions()
        ), kwargs=kwargs))

    def start(self, **kwargs):
        """
        Start all managed instances
        """
        def region_start(region, instances, **kwds):
            resp = region.conn.start_instances(InstanceIds=instances, **kwds)
            return StateChanges(resp['StartingInstances'], region=region)

        return StateChanges.collect(wait((
            partial(region_start, region, instances)
            for region, instances in self.regions()
        ), kwargs=kwargs))

    def terminate(self, **kwargs):
        """
        Terminate all managed instances
        """
        def region_terminate(region, instances, **kwds):
            resp = region.conn.terminate_instances(InstanceIds=instances, **kwds)
            return StateChanges(resp['TerminatingInstances'], region=region)

        return StateChanges.collect(wait((
            partial(region_terminate, region, instances)
            for region, instances in self.regions()
        ), kwargs=kwargs))

    def regions(self):
        """
        Returns the region and all associated instance ids as a tuple. E.g.
        similar to items() but actually does perform some modifications.
        """
        for region, instances in self.data.items():
            yield region, tuple(instances)

    def filter(self, values, regions=False, instances=False):
        """
        Filters managed instance by either regions or instances.
        """
        if not regions and not instances:
            raise ValueError("specify either regions or instances to filter")

        if regions and instances:
            raise ValueError("cannot specify both regions and instances")

        if regions:
            values = frozenset(parse_region(value) for value in values)
            data = {
                region: instances
                for region, instances in self.regions()
                if region in values
            }

        if instances:
            values = frozenset(values)
            data = {
                region: [
                    instance for instance in instances
                    if instance in values
                ]
                for region, instances in self.regions()
            }

        return self.__class__(data)

    def serialize(self):
        return {
            "updated": utcnow(),
            "instances": {
                str(region): list(values)
                for region, values in self.data.items()
            }
        }

    def dump(self, path=INSTANCES):
        """
        Dump the managed instances to the specified path on disk.
        """
        with open(path, 'w') as f:
            json.dump(self, f, cls=Encoder, indent=2)

    def add(self, instance, region):
        self.data[parse_region(region)].add(instance)

    def discard(self, instance, region=None):
        if region:
            self.data[parse_region(region)].discard(instance)
        else:
            # Search for instance to discard
            for instances in self.data.values():
                if instance in instances:
                    instances.discard(instance)
                    break

    def get_region_for_instance(self, instance):
        for region, instances in self.data.items():
            if instance in instances:
                return region
        return None

    def __iter__(self):
        for instances in self.data.values():
            for instance in instances:
                yield instance

    def __contains__(self, instance):
        for instances in self.data.values():
            if instance in instances:
                return True
        return False

    def __len__(self):
        return sum(len(instances) for instances in self.data.values())

    def __repr__(self):
        return "<ManagedInstances containing {}>".format(str(self))

    def __str__(self):
        return "{} instances in {} regions".format(
            len(self), len(self.data)
        )


##########################################################################
## State Changes
##########################################################################

class StateChange(Resource):

    REQUIRED_KEYS = ('CurrentState', 'PreviousState', 'InstanceId')
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    @property
    def previous(self):
        """
        Returns the previous state
        """
        return self["PreviousState"]["Name"]

    @property
    def current(self):
        """
        Returns the current state
        """
        return self["CurrentState"]["Name"]

    def __unicode__(self):
        return u"{} ➟ {}".format(
            color.format(self.previous, Instance.STATE_COLORS[self.previous]),
            color.format(self.current, Instance.STATE_COLORS[self.current]),
        )


class StateChanges(Collection):

    RESOURCE = StateChange


if __name__ == '__main__':
    manager = ManagedInstances.load()
    print(manager)
    print(json.dumps(manager, cls=Encoder, indent=2))
