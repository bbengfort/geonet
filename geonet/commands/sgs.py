# -*- coding: utf-8 -*-
# geonet.commands.sgs
# Create and manage Alia security groups
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Mar 08 17:01:52 2018 -0500
#
# ID: sgs.py [] benjamin@bengfort.com $

"""
Create and manage security groups
"""

##########################################################################
## Imports
##########################################################################

from commis import color
from commis import Command
from tabulate import tabulate

from geonet.region import Regions
from geonet.utils.async import wait
from geonet.config import settings

from functools import partial


GROUP_NAME = "alia"
CHECKMARK  = color.format(u"✓", color.LIGHT_GREEN)
CROSSMARK  = color.format(u"✗", color.LIGHT_RED)


##########################################################################
## Command Description
##########################################################################

class SecurityGroupCreateCommand(Command):

    name = "sg:create"
    help = "create the default alia security group"
    args = {
        '--tablefmt': {
            'choices': ('plain', 'simple', 'pipe', 'psql', 'html', 'latex'),
            'default': 'simple',
            'help': 'markdown table format for display',
        },
        'regions': {
            'choices': settings.regions + ["all"],
            'metavar': 'REGION', 'nargs': "+",
            'help': 'specify regions to create security group',
        },
    }

    def handle(self, args):
        """
        Handle the security group create command
        """

        # Load the regions for the sg command
        regions = Regions.load()

        # Filter regions specified
        args.regions = set(args.regions)
        if "all" not in args.regions:
            regions = Regions(
                region for region in regions
                if str(region) in args.regions
            )

        results = wait(
            (partial(self.handle_region, region) for region in regions),
            args=(args,))

        table = [['', 'Region', 'Notes']] + results
        print(tabulate(table, tablefmt=args.tablefmt, headers='firstrow'))


    def handle_region(self, region, args):
        """
        Create the default security group in the specified region
        """
        result = [CHECKMARK, str(region), "created security group '{}'".format(GROUP_NAME)]

        try:
            # Create the security group
            response = region.conn.create_security_group(
                Description='Security group for Alia replicas and clients.',
                GroupName=GROUP_NAME,
            )

            # Get the newly created group id
            group_id = response["GroupId"]

            # Allow all network traffic from within the security group
            response = region.conn.authorize_security_group_ingress(
                GroupId = group_id,
                IpPermissions = [
                    {
                        "IpProtocol": "tcp", "FromPort": 0, "ToPort": 65535,
                        "UserIdGroupPairs": [
                            {
                                "GroupId": group_id,
                                "Description": "allow all traffic from the same group",
                            }
                        ]
                    }
                ]
            )

            # Open Alia-specific ports for access
            reponse = region.conn.authorize_security_group_ingress(
                GroupId = group_id,
                IpPermissions = [
                    {
                        "IpProtocol": "tcp", "FromPort": 22, "ToPort": 22,
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0",
                                "Description": "allow remote SSH access"
                            }
                        ]
                    },
                    {
                        "IpProtocol": "tcp", "FromPort": 3264, "ToPort": 3285,
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0",
                                "Description": "external Alia service access",
                            }
                        ],
                        "Ipv6Ranges": [
                            {
                                "CidrIpv6": "::/0",
                                "Description": "external Alia service IPv6 access"
                            }
                        ]
                    },
                    {
                        "IpProtocol": "tcp", "FromPort": 5356, "ToPort": 5356,
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0",
                                "Description": "research services access"
                            }
                        ]
                    },
                    {
                        "IpProtocol": "tcp", "FromPort": 4157, "ToPort": 4157,
                        "IpRanges": [
                            {
                                "CidrIp": "0.0.0.0/0",
                                "Description": "master services access",
                            }
                        ]
                    },
                ]
            )


        except Exception as e:
            result[0] = CROSSMARK
            result[2] = str(e)


        return result


class SecurityGroupAuthCommand(Command):

    name = "sg:auth"
    help = "add ingress rule to security group"
    args = {
        '--tablefmt': {
            'choices': ('plain', 'simple', 'pipe', 'psql', 'html', 'latex'),
            'default': 'simple',
            'help': 'markdown table format for display',
        },
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions in which to modify alia security group',
        },
        '--ipaddr': {
            'type': str, 'metavar': 'IPv4/32', 'default': '0.0.0.0/0',
            'help': 'IP address to authorize port for (default is open)',
        },
        'port': {
            'type': int, 'metavar': 'PORT',
            'help': 'port to open in the security group'
        }
    }

    def handle(self, args):
        """
        Handle the port authorization/revoke command
        """
        args.regions = set(args.regions)
        regions = Regions(
            region for region in Regions.load()
            if str(region) in args.regions
        )

        results = wait(
            (partial(self.handle_region, region) for region in regions),
            args=(args,))

        table = [['', 'Region', 'Notes']] + results
        print(tabulate(table, tablefmt=args.tablefmt, headers='firstrow'))

    def handle_region(self, region, args):
        """
        Authorize port in specified region
        """
        result = [
            CHECKMARK, str(region),
            "authorized port {} for {}".format(args.port, args.ipaddr)
        ]

        try:
            reponse = region.conn.authorize_security_group_ingress(
                GroupName = GROUP_NAME,
                FromPort = args.port, ToPort = args.port,
                CidrIp = args.ipaddr, IpProtocol = "tcp",
            )
        except Exception as e:
            result[0] = CROSSMARK
            result[2] = str(e)

        return result


class SecurityGroupRevokeCommand(SecurityGroupAuthCommand):

    name = "sg:revoke"
    help = "revoke ingress rule for security group"

    def handle_region(self, region, args):
        """
        Revoke port in specified region
        """
        result = [
            CHECKMARK, str(region),
            "revoked port {} for {}".format(args.port, args.ipaddr)
        ]

        try:
            reponse = region.conn.revoke_security_group_ingress(
                GroupName = GROUP_NAME,
                FromPort = args.port, ToPort = args.port,
                CidrIp = args.ipaddr, IpProtocol = "tcp",
            )
        except Exception as e:
            result[0] = CROSSMARK
            result[2] = str(e)

        return result


class SecurityGroupDestroyCommand(Command):

    name = "sg:destroy"
    help = "delete security group from specified region"
    args = {
        '--tablefmt': {
            'choices': ('plain', 'simple', 'pipe', 'psql', 'html', 'latex'),
            'default': 'simple',
            'help': 'markdown table format for display',
        },
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions in which to modify alia security group',
        },
    }

    def handle(self, args):
        """
        Handle the sg:destroy command
        """
        args.regions = set(args.regions)
        regions = Regions(
            region for region in Regions.load()
            if str(region) in args.regions
        )

        results = wait(
            (partial(self.handle_region, region) for region in regions),
            args=(args,))

        table = [['', 'Region', 'Notes']] + results
        print(tabulate(table, tablefmt=args.tablefmt, headers='firstrow'))

    def handle_region(self, region, args):
        """
        Destroys the default security group in the specified region
        """
        result = [
            CHECKMARK, str(region), "destroyed security group '{}'".format(GROUP_NAME)
        ]

        try:
            resp = region.conn.delete_security_group(GroupName=GROUP_NAME)
        except Exception as e:
            result[0] = CROSSMARK
            result[2] = str(e)

        return result
