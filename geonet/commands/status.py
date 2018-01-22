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


##########################################################################
## Status Lights
##########################################################################

LIGHTS = {
    Instance.PENDING: color.format(u"●", color.YELLOW),
    Instance.RUNNING: color.format(u"●", color.GREEN),
    Instance.SHUTTING_DOWN: color.format(u"●", color.CYAN),
    Instance.TERMINATED: color.format(u"●", color.BLUE),
    Instance.STOPPING: color.format(u"●", color.LIGHT_RED),
    Instance.STOPPED: color.format(u"●", color.RED),
}


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
        regions = Regions.load()

        for region in args.regions:

            # Get region data
            region = regions.find(region)
            if region is None: continue

            # Handle the status for the region
            self.handle_region(region, args)


    def handle_region(self, region, args):
        """
        Lists the instance in the specified region
        """
        output = []
        instances = region.instances()
        instances.sortby('name')

        header = u"{} ({} instances)".format(region.locale, len(instances))
        output.extend([header, "-"*len(header)])

        for instance in instances:
            output.append(
                u"  {} {}".format(LIGHTS[instance.state], instance.name)
            )

        output.append("")
        print("\n".join(output))
