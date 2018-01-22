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

import os
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

    REQUIRED_KEYS = ('State', 'Tags')

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

    REQUIRED_KEYS = ('KeyName', 'KeyFingerprint')
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    @property
    def name(self):
        return self["KeyName"]

    @property
    def fingerprint(self):
        return self["KeyFingerprint"]

    def local_path(self, sshdir=None):
        """
        Returns the expected local path of the key in the specified directory.
        If None is passed in, uses the default user SSH directory.
        """
        sshdir = sshdir or os.path.expanduser(os.path.join("~", ".ssh"))
        return os.path.join(sshdir, "{}.pem".format(self.name))

    def has_valid_key(self, sshdir=None):
        """
        Returns true if there is a key at the local path, its permisisons are
        set to 0600.
        """
        # TODO: also verify fingerprint
        path = self.local_path(sshdir)
        if os.path.exists(path):
            if oct(os.stat(path).st_mode & 0777) == '0600':
                return True
        return False


class KeyPairs(Collection):

    RESOURCE = KeyPair


##########################################################################
## Launch Templates
##########################################################################

class LaunchTemplate(Resource):

    REQUIRED_KEYS = None
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    @property
    def name(self):
        return self["LaunchTemplateName"]

    @property
    def version(self):
        return int(self["LatestVersionNumber"])

    def __str__(self):
        return self["LaunchTemplateId"]


class LaunchTemplates(Collection):

    RESOURCE = LaunchTemplate


##########################################################################
## Images
##########################################################################

class Image(Resource):

    REQUIRED_KEYS = None
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    @property
    def name(self):
        return self["Name"]

    @property
    def size(self):
        # TODO: make this less fragile
        return self["BlockDeviceMappings"][0]["Ebs"]["VolumeSize"]

    @property
    def disk(self):
        # TODO: make this less fragile
        return self["BlockDeviceMappings"][0]["Ebs"]["VolumeType"]

    def __str__(self):
        return self["ImageId"]


class Images(Collection):

    RESOURCE = Image


##########################################################################
## Security Groups
##########################################################################

class SecurityGroup(Resource):

    REQUIRED_KEYS = ["GroupId", "GroupName", "IpPermissions"]
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    @property
    def name(self):
        return self["GroupName"]

    def open_ip_permissions(self):
        """
        Return all permissions open to 0.0.0.0/0
        """

        def is_open(perm):
            for rng in perm["IpRanges"]:
                if rng["CidrIp"] == "0.0.0.0/0":
                    return True
            return False

        for perm in self["IpPermissions"]:
            if is_open(perm):
                yield perm

    def open_ports(self):
        """
        Returns ports open to world
        """
        for perm in self.open_ip_permissions():
            fp = perm["FromPort"]
            tp = perm["ToPort"]

            if fp == tp:
                yield fp
            else:
                yield (fp, tp)

    def __str__(self):
        return self["GroupId"]

class SecurityGroups(Collection):

    RESOURCE = SecurityGroup
