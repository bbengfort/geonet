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
PLACEMENTS = "placement-groups"
ZONES = "availability-zones"


# Checks
CHECKS = {
    True: color.format(u"✓", color.LIGHT_GREEN),
    False: color.format(u"✗", color.LIGHT_RED)
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

    if s in {'p', 'pg', 'pgs', 'placement', 'placements', 'placement-group', PLACEMENTS}:
        return PLACEMENTS

    if s in {'z', 'az', 'azs', 'zone', 'zones', 'availability-zone', ZONES}:
        return ZONES


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
            'choices': (INSTANCES, VOLUMES, GROUPS, TEMPLATES, AMIS, KEYS, PLACEMENTS, ZONES),
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

        table = [["State", "Region", "Zone", "Instance", "Name", "Type", "IP Addr",]]

        for instance in instances:
            table.append([
                instance.state_light(), instance.region.name, instance.zone,
                str(instance), instance.name, instance.vm_type, instance.ipaddr,
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
                volume.state_light(), volume.region.name,
                str(volume), volume.name,
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


    def handle_placement_groups(self, args):
        """
        Describe placement groups in each region
        """
        groups = self.regions.placement_groups()
        if args.debug:
            print(to_json(groups, indent=2))
            return

        table = [["Region", "Name", "State", "Strategy", "Partition Count"]]

        for group in groups:
            table.append([
                group.region.name, group.name, group.state, group.strategy, group.partition_count(),
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
            version = "v{} (r{})".format(
                template.default_version, template.latest_version
            )

            table.append([
                template.region.name, str(template), template.name, version,
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

    def handle_availability_zones(self, args):
        """
        Describe availability zones in each region
        """
        zones = self.regions.zones()
        if args.debug:
            print(to_json(zones, indent=2))
            return

        table = [["Region", "Name", "State", "Messages"]]
        for zone in zones:
            table.append([
                zone.region.name, zone.name, zone.state, ", ".join(list(zone.messages()))
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))