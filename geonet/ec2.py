# -*- coding: utf-8 -*-
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
from geonet.utils.timez import parse_datetime
from geonet.utils.timez import utcnow, humanizedelta

from commis import color
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

    # State constants
    PENDING       = 'pending'
    RUNNING       = 'running'
    SHUTTING_DOWN = 'shutting-down'
    TERMINATED    = 'terminated'
    STOPPING      = 'stopping'
    STOPPED       = 'stopped'

    # State light colors
    STATE_COLORS = {
        'pending': color.YELLOW,
        'running': color.GREEN,
        'shutting-down': color.CYAN,
        'terminated': color.BLUE,
        'stopping': color.LIGHT_RED,
        'stopped': color.RED,
    }


    def __init__(self, *args, **kwargs):
        super(Instance, self).__init__(*args, **kwargs)
        self.status = None

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

    @property
    def vm_type(self):
        return self["InstanceType"]

    @property
    def ipaddr(self):
        for key in ("PublicIpAddress", "PrivateIpAddress"):
            if key in self:
                return self[key]
        return None

    @property
    def hostname(self):
        for key in ('PublicDnsName', 'PrivateDnsName'):
            if key in self:
                return self[key]
        return None

    def uptime(self):
        """
        Returns the time since launch (not necessarily the time running)
        """
        if self.state != Instance.RUNNING:
            return None

        delta = utcnow() - self["LaunchTime"]
        return humanizedelta(seconds=delta.total_seconds())

    def state_light(self, full=True):
        """
        Returns the colorized state light. If full is true, returns the name.
        """
        scolor = self.STATE_COLORS[self.state]
        if full:
            return color.format(u"● {}", scolor, self.state)
        return color.format(u"●", scolor)

    def __str__(self):
        return self["InstanceId"]


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

    def update_statuses(self):
        """
        Update the instance statuses for the given instances.
        """
        if not self.region or isinstance(self.region, basestring):
            raise TypeError("cannot update status with no region connection")

        # TODO: validate response
        resp = self.region.conn.describe_instance_status(
            InstanceIds = [str(instance) for instance in self],
            IncludeAllInstances = False,
        )

        for status in resp["InstanceStatuses"]:
            self[status["InstanceId"]].status = status



##########################################################################
## Volumes
##########################################################################

class Volume(Resource):

    REQUIRED_KEYS = None
    EXTRA_KEYS    = None
    EXTRA_DEFAULT = None

    # State constants
    CREATING  = 'creating'
    AVAILABLE = 'available'
    IN_USE    = 'in-use'
    DELETING  = 'deleting'
    DELETED   = 'deleted'
    ERROR     = 'error'

    STATE_COLORS = {
        'creating': color.YELLOW,
        'available': color.CYAN,
        'in-use': color.GREEN,
        'deleting': color.LIGHT_BLUE,
        'deleted': color.BLUE,
        'error': color.RED,
    }

    @property
    def state(self):
        return self["State"]

    @property
    def size(self):
        return self["Size"]

    def attached_to(self):
        """
        Returns instance id strings of any attachments
        """
        for attached in self["Attachments"]:
            if attached["State"] in {"attached", "attaching"}:
                yield attached["InstanceId"]

    def state_light(self, full=True):
        """
        Returns the colorized state light. If full is true, returns the name.
        """
        scolor = self.STATE_COLORS[self.state]
        if full:
            return color.format(u"● {}", scolor, self.state)
        return color.format(u"●", scolor)


    def __str__(self):
        return self["VolumeId"]


class Volumes(Collection):

    RESOURCE = Volume


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

    def __str__(self):
        return self.name


class KeyPairs(Collection):

    RESOURCE = KeyPair

    def get_alia_keys(self):
        """
        Returns any key pairs prefixed by alia.
        """
        return [
            key for key in self
            if key.name.startswith("alia")
        ]


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
    def latest_version(self):
        return int(self["LatestVersionNumber"])

    @property
    def default_version(self):
        return int(self["DefaultVersionNumber"])

    def __str__(self):
        return self["LaunchTemplateId"]


class LaunchTemplates(Collection):

    RESOURCE = LaunchTemplate

    def get_alia_template(self, region):
        for template in self:
            if template.name == "alia" and template.region == region:
                return template

    def sort_latest(self):
        self.items.sort(key=itemgetter("CreateTime"), reverse=True)
        return self


##########################################################################
## Images
##########################################################################

class Image(Resource):

    REQUIRED_KEYS = ["ImageId", "BlockDeviceMappings", "CreationDate"]
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

    @property
    def created(self):
        return parse_datetime(self["CreationDate"])

    def __str__(self):
        return self["ImageId"]


class Images(Collection):

    RESOURCE = Image

    def sort_latest(self):
        self.items.sort(key=attrgetter("created"), reverse=True)
        return self

    def get_alia_images(self):
        """
        Returns any images prefixed by alia.
        """
        return [
            image for image in self
            if image.name.startswith("alia")
        ]


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

    def get_alia_groups(self):
        """
        Returns any security groups prefixed by alia.
        """
        return [
            group for group in self
            if group.name.startswith("alia")
        ]
