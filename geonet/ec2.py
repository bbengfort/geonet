# geonet.ec2
# Helpers for connecting to EC2 regions with boto
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 12:31:57 2018 -0500
#
# ID: ec2.py [] benjamin@bengfort.com $

"""
Helpers for connecting to EC2 regions with boto
"""

##########################################################################
## Imports
##########################################################################

import json
import boto3

from geonet.config import settings
from geonet.base import Resource, Collection

from collections import defaultdict
from operator import itemgetter, attrgetter


##########################################################################
## Helper Methods
##########################################################################

def connect(region=None, **kwargs):
    """
    Create a boto connection to the specified region that closes when done.
    Pass any kwargs to the boto.ec2.connect_to_region function, and defaults
    will be collected from the primary configuration.
    """
    # Get default region if required
    region = region or settings.aws.aws_region

    # Create default configuration arguments
    options = dict(settings.aws.options())
    options.update(kwargs)
    return boto3.client('ec2', region_name=str(region), **kwargs)


##########################################################################
## Instances
##########################################################################

class Instance(Resource):

    REQUIRED_KEYS = ['State', 'Tags']

    PENDING       = 'pending'
    RUNNING       = 'running'
    SHUTTING_DOWN = 'shutting-down'
    TERMINATED    = 'terminated'
    STOPPING      = 'stopping'
    STOPPED       = 'stopped'

    @property
    def state(self):
        """
        Returns the instances current state
        """
        return self['State']['Name']

    @property
    def name(self):
        """
        Figures out the instance name by first looking in the tags, then
        returning the public or private IP address.
        """
        for tag in self.data.get('Tags', []):
            if tag["Key"] == "Name":
                return tag["Value"]

        lookups = (
            "PublicDnsName", "PublicIpAddress",
            "PrivateDnsName", "PrivateIpAddress"
        )

        for key in lookups:
            if key in self:
                return self[key]

        return ""


class Instances(Collection):

    RESOURCE = Instance

    def states(self):
        """
        Returns a dictionary of states to instances
        """
        status = defaultdict(list)
        for instance in self:
            status[instance.state].append(instance)
        return status

    def with_states(self, states):
        """
        Yields all instances with the specified state or states.
        """
        if isinstance(states, basestring):
            states = (states,)
        states = frozenset(states)

        for instance in self:
            if instance.state in states:
                yield instance

    def running(self):
        """
        Filters instances that are currently running
        """
        return self.with_states(Instance.RUNNING)

    def sortby(self, key, reverse=False):
        """
        Sort the instances by the specified key
        """
        attrs = frozenset(('name', 'state'))
        func = attrgetter(key) if key in attrs else itemgetter(key)
        self.items.sort(key=func, reverse=reverse)


##########################################################################
## Key Pairs
##########################################################################

class KeyPair(Resource):

    REQUIRED_KEYS = ['KeyName', 'KeyFingerprint']
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None


class KeyPairs(Collection):

    RESOURCE = KeyPair


##########################################################################
## Launch Templates
##########################################################################

class LaunchTemplate(Resource):

    REQUIRED_KEYS = None
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None


class LaunchTemplates(Collection):

    RESOURCE = LaunchTemplate


##########################################################################
## Images
##########################################################################

class Image(Resource):

    REQUIRED_KEYS = None
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None


class Images(Collection):

    RESOURCE = Image


##########################################################################
## Security Groups
##########################################################################

class SecurityGroup(Resource):

    REQUIRED_KEYS = None
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None


class SecurityGroups(Collection):

    RESOURCE = SecurityGroup
