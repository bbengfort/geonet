# -*- coding: utf-8 -*-
# geonet.commands.status
# Lists the status of all instances in all regions.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 17:45:54 2018 -0500
#
# ID: status.py [] benjamin@bengfort.com $

"""
Lists the status of all instances in all regions.
"""

##########################################################################
## Imports
##########################################################################

from commis import color
from commis import Command
from tabulate import tabulate

from geonet.config import settings
from geonet.managed import ManagedInstances


##########################################################################
## Command Description
##########################################################################

class StatusCommand(Command):

    name = "status"
    help = "lists the status of managed instances"
    args = {
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions to get the status for',
        },
        'instances': {
            'nargs': '*', 'default': None, 'metavar': 'instance',
            'help': 'specify the instances to list the status for',
        },
    }

    def handle(self, args):
        """
        Handles the config command with arguments from the command line.
        """
        # Load the instance manager
        manager = ManagedInstances.load()

        # Filter by regions
        manager = manager.filter(args.regions, regions=True)

        # Filter by instance ids
        if args.instances:
            manager = manager.filter(args.instances, instances=True)

        # Return if no instances are managed
        if len(manager) == 0:
            return color.format(
                "no instances under management", color.LIGHT_YELLOW
            )

        # Load the instances
        instances = manager.status()

        # Create the region table
        table = [
            [
                instance.state_light(),
                instance.region.name,
                instance.name, str(instance),
                instance.uptime()

            ]
            for instance in instances
        ]

        print(tabulate(table, tablefmt="plain"))
