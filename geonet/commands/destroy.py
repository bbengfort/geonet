# geonet.commands.destroy
# Destroy all instances under management
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 23 18:10:54 2018 -0500
#
# ID: destroy.py [] benjamin@bengfort.com $

"""
Destroy all instances under management
"""

##########################################################################
## Imports
##########################################################################

import sys

from commis import color
from commis import Command

from geonet.region import Regions
from geonet.managed import ManagedInstances

from collections import defaultdict


##########################################################################
## Destroy Command
##########################################################################

class DestroyCommand(Command):

    name = "destroy"
    help = "destroy instances under management"
    args = {
        ('-f', '--force'): {
            'action': 'store_true', 'help': 'do not prompt before destroying',
        },
        'instances': {
            'nargs': '*', 'default': None, 'metavar': 'instance',
            'help': 'specify the instances to be destroyed',
        }
    }

    def handle(self, args):
        """
        Handle the destroy command
        """
        # Load the managed instances
        manager = ManagedInstances.load()

        # Validate instances and create a new manager
        if args.instances:
            regions = defaultdict(list)
            n_unmanaged = 0
            # Validate instances are managed
            for instance in args.instances:
                if instance not in manager:
                    n_unmanaged += 1

                for region, instances in manager.regions():
                    if instance in instances:
                        regions[region].append(instance)
                        break

            if n_unmanaged > 0:
                raise ValueError(
                    "cannot destroy {} unmanaged instances".format(n_unmanaged)
                )

            manager = ManagedInstances(regions)

        # Prompt to confirm
        if not args.force:
            if not self.prompt("destroy {}?".format(manager)):
                print(color.format("stopping instance termination", color.LIGHT_YELLOW))
                return

        # Destroy instances

        # Report destruction

        # Remove instances from management


    def prompt(self, prompt, default='no'):
        """
        Request yes/no user input and return a bool.
        """
        valid = {
            'y': True, 'yes': True, 'ye': True,
            'n': False, 'no': False, 'neg': False,
        }

        if default is None:
            vals = " [y/n] "
        elif default == 'yes':
            vals = " [Y/n] "
        elif default == 'no':
            vals = " [y/N] "
        else:
            raise ValueError("invalid default answer: '{}'".format(default))

        while True:
            sys.stdout.write(prompt + vals)
            choice = raw_input().lower()
            if default is not None and choice == '':
                return valid[default]
            elif choice in valid:
                return valid[choice]
            else:
                sys.stdout.write('invalid response; ')
