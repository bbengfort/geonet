# -*- coding: utf-8 -*-
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
from tabulate import tabulate

from geonet.managed import ManagedInstances


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
            n_unmanaged = 0
            for instance in args.instances:
                if instance not in manager:
                    n_unmanaged += 1

            # Cannot destroy any unmanaged instances
            if n_unmanaged > 0:
                raise ValueError(
                    "cannot destroy {} unmanaged instances".format(n_unmanaged)
                )

            # Filter the manager to the instances we'll be destroying
            manager = manager.filter(args.instances, instances=True)

        # Return if no instances are managed
        if len(manager) == 0:
            return color.format(
                "no instances under management", color.LIGHT_YELLOW
            )

        # Prompt to confirm
        if not args.force:
            prompt = color.format("destroy {}?", color.LIGHT_YELLOW, manager)
            if not self.prompt(prompt):
                print(color.format("stopping instance termination", color.LIGHT_CYAN))
                return
            print(color.format(u"destroying {} instances …\n", color.LIGHT_RED, len(manager)))

        # Destroy instances
        reports = manager.terminate()

        # Report destruction
        table = [['Region', 'Instance', 'State']]
        table.extend([
            [
                report.region.name, report["InstanceId"], unicode(report),
            ]
            for report in reports
        ])
        print(tabulate(table, tablefmt="simple", headers='firstrow'))

        # Remove instances from management
        # Ensure we reload the full manager list and not use the filtered one.
        manager = ManagedInstances.load()
        for report in reports:
            manager.discard(report["InstanceId"])
        manager.dump()

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
