# -*- coding: utf-8 -*-
# geonet.commands.descr
# Describes available resources and resource types
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Fri Jan 19 07:47:20 2018 -0500
#
# ID: descr.py [] benjamin@bengfort.com $

"""
Describes available resources and resource types
"""

##########################################################################
## Imports
##########################################################################

from commis import color
from commis import Command
from tabulate import tabulate

from geonet.region import Regions
from geonet.utils.timer import Timer
from geonet.ec2 import Instance, Volume
from geonet.utils.serialize import to_json

# Resource Types
GROUPS = "security-groups"
TEMPLATES = "launch-templates"
AMIS = "images"
KEYS = "key-pairs"
VOLUMES = "volumes"
INSTANCES = "instances"


# Checks
CHECKS = {
    True: color.format(u"✓", color.LIGHT_GREEN),
    False: color.format(u"✗", color.LIGHT_RED)
}

# States
STATES = {
    # Volume States
    Volume.CREATING: color.format(u"●", color.YELLOW),
    Volume.AVAILABLE: color.format(u"●", color.CYAN),
    Volume.IN_USE: color.format(u"●", color.GREEN),
    Volume.DELETING: color.format(u"●", color.LIGHT_BLUE),
    Volume.DELETED: color.format(u"●", color.BLUE),
    Volume.ERROR: color.format(u"●", color.RED),

    # Instance States
    Instance.PENDING: color.format(u"●", color.YELLOW),
    Instance.RUNNING: color.format(u"●", color.GREEN),
    Instance.SHUTTING_DOWN: color.format(u"●", color.CYAN),
    Instance.TERMINATED: color.format(u"●", color.BLUE),
    Instance.STOPPING: color.format(u"●", color.LIGHT_RED),
    Instance.STOPPED: color.format(u"●", color.RED),
}


##########################################################################
## Helper Methods
##########################################################################

def rtype(s):
    """
    Compute aliases for the resource type
    """
    s = s.lower()

    if s in {'m', 'machine', 'machines', 'vm', 'vms', 'instance', INSTANCES}:
        return INSTANCES

    if s in {'v', 'vols', 'volume', VOLUMES}:
        return VOLUMES

    if s in {'t', 'template', 'templates', 'lt', 'launch-template', TEMPLATES}:
        return TEMPLATES

    if s in {'s', 'sg', 'sgs', 'group', 'groups', 'security-group', GROUPS}:
        return GROUPS

    if s in {'i', 'image', 'ami', 'amis', AMIS}:
        return AMIS

    if s in {'k', 'keys', 'key-pair', KEYS}:
        return KEYS


##########################################################################
## Command Description
##########################################################################

class DescribeCommand(Command):

    name = "descr"
    help = "describe available ec2 resources"
    args = {
        '--debug': {
            'action': 'store_true',
            'help': 'print json response from AWS and exit',
        },
        ('-f', '--format'): {
            'choices': ('plain', 'simple', 'pipe', 'psql', 'html', 'latex'),
            'default': 'simple',
            'help': 'markdown table format for display',
        },
        ('-T', '--timer'): {
            'action': 'store_true', 'help': 'print total request time',
        },
        ('-R', '--all-regions'): {
            'action': 'store_true', 'help': 'use all regions not just active ones',
        },
        'resource': {
            'choices': (INSTANCES, VOLUMES, GROUPS, TEMPLATES, AMIS, KEYS),
            'type': rtype, 'help': 'name of resource type to describe',
        },
    }

    def handle(self, args):
        """
        Handles the config command with arguments from the command line.
        """
        self.regions = Regions.load() if args.all_regions else Regions.load_active()

        with Timer() as timer:
            method = "handle_{}".format(args.resource.replace("-", "_"))
            getattr(self, method)(args)

        if args.timer:
            print("request took {}".format(timer))

    def handle_instances(self, args):
        """
        Describe instances in each region
        """
        instances = self.regions.instances()
        if args.debug:
            print(to_json(instances, indent=2))

        table = [["", "Region", "Instance", "Name", "Type", "IP Addr",]]

        for instance in instances:
            table.append([
                STATES[instance.state], instance.region.name, str(instance),
                instance.name, instance.vm_type, instance.ipaddr,
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))

    def handle_volumes(self, args):
        """
        Describe volumes in each region
        """
        volumes = self.regions.volumes()
        if args.debug:
            print(to_json(volumes, indent=2))

        table = [["State", "Region", "Volume", "Name",  "Attached"]]

        for volume in volumes:
            table.append([
                STATES[volume.state], volume.region.name, str(volume), volume.name,
                ", ".join(list(volume.attached_to()))
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))

    def handle_security_groups(self, args):
        """
        Describe security groups in each region
        """
        groups = self.regions.security_groups()
        if args.debug:
            print(to_json(groups, indent=2))
            return

        table = [["Region", "Group", "Name", "Ports"]]

        for group in groups:
            ports = ", ".join([
                "{}-{}".format(*p) if isinstance(p, tuple) else str(p)
                for p in group.open_ports()
            ])

            table.append([
                group.region.name, str(group), group.name, ports
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))


    def handle_launch_templates(self, args):
        """
        Describe launch templates in each region
        """
        templates = self.regions.launch_templates()
        if args.debug:
            print(to_json(templates, indent=2))
            return

        table = [["Region", "Template", "Name", "Version"]]
        for template in templates:
            table.append([
                template.region.name, str(template), template.name,
                template.version
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))

    def handle_images(self, args):
        """
        Describe AMI images available in each region
        """
        images = self.regions.images()
        if args.debug:
            print(to_json(images, indent=2))
            return

        table = [["Region", "AMI", "Name", "Size", "Disk"]]
        for image in images:
            table.append([
                image.region.name, str(image), image.name, image.size, image.disk
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))

    def handle_key_pairs(self, args):
        """
        Describe key pairs available in each region
        """
        pairs = self.regions.key_pairs()
        if args.debug:
            print(to_json(pairs, indent=2))
            return

        table = [["Region", "Name", "Fingerprint", "Valid Local"]]

        for key in pairs:
            table.append([
                key.region.name, key.name, key.fingerprint,
                CHECKS[key.has_valid_key()]
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))
