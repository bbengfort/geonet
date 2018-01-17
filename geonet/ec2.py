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
