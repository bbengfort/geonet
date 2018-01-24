# -*- coding: utf-8 -*-
# geonet.commands.stop
# Stop instances under management
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 23:33:01 2018 -0500
#
# ID: stop.py [] benjamin@bengfort.com $

"""
Stop instances under management
"""

##########################################################################
## Imports
##########################################################################

from commis import Command
from tabulate import tabulate

from geonet.config import settings
from geonet.managed import ManagedInstances


##########################################################################
## Stop Command
##########################################################################

class StopCommand(Command):

    name = "stop"
    help = "stop instances under management"
    args = {
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions to stop instances of',
        },
        'instances': {
            'nargs': '*', 'default': None, 'metavar': 'instance',
            'help': 'specify the instances to stop',
        },
    }

    def handle(self, args):
        """
        Stop all instances using the managed instances
        """
        manager = ManagedInstances.load()

        # Filter by regions
        manager = manager.filter(args.regions, regions=True)

        # Filter by instance ids
        if args.instances:
            manager = manager.filter(args.instances, instances=True)

        table = [
            [
                report["InstanceId"],
                u"{} ➟ {}".format(
                    report["PreviousState"]["Name"],
                    report["CurrentState"]["Name"]
                )
            ]
            for report in manager.stop()
        ]
        print(tabulate(table, tablefmt="plain"))
