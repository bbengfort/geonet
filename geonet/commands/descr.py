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
from geonet.region import Regions
from geonet.utils.timer import Timer
from geonet.utils.serialize import to_json
from geonet.ec2 import SecurityGroups, KeyPairs
from geonet.ec2 import Images, LaunchTemplates
from tabulate import tabulate


# Resource Types
GROUPS = "security-groups"
TEMPLATES = "launch-templates"
AMIS = "images"
KEYS = "key-pairs"

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
    if s in {'s', 'sg', 'sgs', 'group', 'groups', 'security-group', GROUPS}:
        return GROUPS

    if s in {'t', 'template', 'templates', 'lt', 'launch-template', TEMPLATES}:
        return TEMPLATES

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
        'resource': {
            'choices': (GROUPS, TEMPLATES, AMIS, KEYS), 'type': rtype,
            'help': 'name of resource type to describe',
        },
    }

    def handle(self, args):
        """
        Handles the config command with arguments from the command line.
        """
        with Timer() as timer:
            self.regions = Regions.load()
            method = "handle_{}".format(args.resource.replace("-", "_"))
            getattr(self, method)(args)

        if args.timer:
            print("request took {}".format(timer))


    def handle_security_groups(self, args):
        """
        Describe security groups in each region
        """
        groups = SecurityGroups.collect(
            region.security_groups() for region in self.regions
        )
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
                group.region, str(group), group.name, ports
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))


    def handle_launch_templates(self, args):
        """
        Describe launch templates in each region
        """
        templates = LaunchTemplates.collect(
            region.launch_templates() for region in self.regions
        )
        if args.debug:
            print(to_json(templates, indent=2))
            return

        table = [["Region", "Template", "Name", "Version"]]
        for template in templates:
            table.append([
                template.region, str(template), template.name, template.version
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))

    def handle_images(self, args):
        """
        Describe AMI images available in each region
        """
        images = Images.collect(
            region.images() for region in self.regions
        )
        if args.debug:
            print(to_json(images, indent=2))
            return

        table = [["Region", "AMI", "Name", "Size", "Disk"]]
        for image in images:
            table.append([
                image.region, str(image), image.name, image.size, image.disk
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))

    def handle_key_pairs(self, args):
        """
        Describe key pairs available in each region
        """
        pairs = KeyPairs.collect(
            region.key_pairs() for region in self.regions
        )
        if args.debug:
            print(to_json(pairs, indent=2))
            return

        table = [["Region", "Name", "Fingerprint", "Valid Local"]]

        for key in pairs:
            table.append([
                key.region, key.name, key.fingerprint,
                CHECKS[key.has_valid_key()]
            ])

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))