# -*- coding: utf-8 -*-
# geonet.commands.start
# Start instances under management
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 23:37:00 2018 -0500
#
# ID: start.py [] benjamin@bengfort.com $

"""
Start instances under management
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
## Start Command
##########################################################################

class StartCommand(Command):

    name = "start"
    help = "start instances under management"
    args = {
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions to start instances of',
        },
        'instances': {
            'nargs': '*', 'default': None, 'metavar': 'instance',
            'help': 'specify the instances to start',
        },
    }

    def handle(self, args):
        """
        Start all instances currently being managed.
        """
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

        table = [['Region', 'Instance', 'State']]
        table.extend([
            [
                report.region.name, report["InstanceId"], unicode(report),
            ]
            for report in manager.start()
        ])
        print(tabulate(table, tablefmt="simple", headers='firstrow'))

        # TODO: update hosts information for SSH
