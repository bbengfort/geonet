# -*- coding: utf-8 -*-
# geonet.zone
# Helpers for describing Availability Zones with Boto
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Mar 25 10:51:30 2019 -0400
#
# ID: zone.py [] benjamin@bengfort.com $

"""
Helpers for connecting to EC2 regions with boto
"""

##########################################################################
## Imports
##########################################################################

from geonet.base import Resource, Collection


##########################################################################
## Availability Zones
##########################################################################

class AvailabilityZone(Resource):

    REQUIRED_KEYS = ["ZoneName", "State", "ZoneId"]
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    @property
    def name(self):
        return self["ZoneName"]

    @property
    def state(self):
        return self["State"]

    @property
    def strategy(self):
        return self["Strategy"]

    def messages(self):
        try:
            for message in self["Messages"]:
                yield message["Message"]
        except KeyError:
            pass

    def __str__(self):
        return self.name or self["ZoneId"]


class AvailabilityZones(Collection):

    RESOURCE = AvailabilityZone

    def get_available(self):
        """
        Returns any zones whose state is available
        """
        return [
            zone for zone in self
            if zone.state.lower() == "available"
        ]