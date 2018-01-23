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

from geonet.managed import ManagedInstances


##########################################################################
## Stop Command
##########################################################################

class StopCommand(Command):

    name = "stop"
    help = "stop instances under management"
    args = {}

    def handle(self, args):
        """
        Stop all instances using the managed instances
        """
        manager = ManagedInstances.load()
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
