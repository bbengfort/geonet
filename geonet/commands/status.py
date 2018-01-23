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

from geonet.ec2 import Instance
from geonet.region import Regions
from geonet.config import settings
from geonet.utils.async import wait

from functools import partial
from tabulate import tabulate


##########################################################################
## Status Lights
##########################################################################

LIGHTS = {
    Instance.PENDING: color.YELLOW,
    Instance.RUNNING: color.GREEN,
    Instance.SHUTTING_DOWN: color.CYAN,
    Instance.TERMINATED: color.BLUE,
    Instance.STOPPING: color.LIGHT_RED,
    Instance.STOPPED: color.RED,
}

def instance_state_light(state):
    return color.format(u"● {}", LIGHTS[state], state)


##########################################################################
## Command Description
##########################################################################

class StatusCommand(Command):

    name = "status"
    help = "lists the status of all instances in all regions"
    args = {
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions to get the status for',
        }
    }

    def handle(self, args):
        """
        Handles the config command with arguments from the command line.
        """
        # Load the regions list
        regions = Regions(
            region for region in Regions.load()
            if str(region) in args.regions
        )

        # Load the instances
        instances = regions.instances()

        # Create the region table
        table = [
            [
                instance_state_light(instance.state),
                instance.region.name,
                instance.name, str(instance),
                instance.uptime()

            ]
            for instance in instances
        ]

        print(tabulate(table, tablefmt="plain"))
