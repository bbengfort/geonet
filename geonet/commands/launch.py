# geonet.commands.launch
# Launch instances using the specified template.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 22:58:36 2018 -0500
#
# ID: launch.py [] benjamin@bengfort.com $

"""
Launch instances using the specified template.
"""

##########################################################################
## Imports
##########################################################################

from commis import Command

from geonet.region import Regions
from geonet.config import settings
from geonet.utils.async import wait

from functools import partial


##########################################################################
## Luanch Command
##########################################################################

class LaunchCommand(Command):

    name = "launch"
    help = "launch instances using the alia template"
    args = {
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions to get the status for',
        },
        "N": {
            'type': int, 'help': 'number of instances to launch',
        }
    }

    def handle(self, args):
        """
        Handle the launch command
        """

        # Load the regions for the launch command
        regions = Regions(
            region for region in Regions.load()
            if str(region) in args.regions
        )

        # Get the templates associated with each region
        self.templates = regions.launch_templates()

        # Launch the instances with the specified template
        results = wait(
            (partial(self.launch_in_region, region) for region in regions),
            args=(args,)
        )

        # Update the instances under management

        # Rename all of the instances

        # Report what went down

    def launch_in_region(self, region, args):
        """
        Launch the specified number of replicas in the given region
        """
        template = self.templates.get_alia_template(region)
        print(region, template, args.N)
