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

from commis import Command
from tabulate import tabulate

from geonet.managed import ManagedInstances


##########################################################################
## Start Command
##########################################################################

class StartCommand(Command):

    name = "start"
    help = "start instances under management"
    args = {}

    def handle(self, args):
        """
        Start all instances currently being managed.
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
            for report in manager.start()
        ]
        print(tabulate(table, tablefmt="plain"))
