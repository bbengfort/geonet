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

from commis import Command
from geonet.ec2 import connect
from geonet.config import settings


##########################################################################
## Command Description
##########################################################################

class StatusCommand(Command):

    name = "status"
    help = "lists the status of all instances in all regions"
    args = {}

    def handle(self, args):
        """
        Handles the config command with arguments from the command line.
        """
        for region in settings.regions:
            self.handle_region(region, args)


    def handle_region(self, region, args):
        """
        Lists the instance in the specified region
        """
        print("{}\n{}\n".format(region.upper(), "-"*len(region)))
        conn = connect(region)
        for res in conn.describe_instances()['Reservations']:
            for instance in res['Instances']:
                print(instance['Tags'])
