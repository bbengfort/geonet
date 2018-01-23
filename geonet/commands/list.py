# geonet.commands.list
# List and edit the instances under management.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 23:23:04 2018 -0500
#
# ID: list.py [] benjamin@bengfort.com $

"""
List and edit the instances under management.
"""

##########################################################################
## Imports
##########################################################################

import os

from commis import Command

from geonet.config import USERCONFIG
from geonet.utils.editor import edit_file
from geonet.managed import ManagedInstances, INSTANCES

from tabulate import tabulate


##########################################################################
## List Command
##########################################################################

class ListCommand(Command):

    name = "list"
    help = "list and edit instances under management"
    args = {
        ('-e', '--edit'): {
            'action': 'store_true', 'default': False,
            'help': 'edit the configuration file and exit',
        }
    }

    def handle(self, args):
        """
        Handles the config command with arguments from the command line.
        """
        if args.edit: self.edit()
        instances = ManagedInstances.load()
        for region, instances in instances.regions():
            table = [[region.name]]
            table.extend([[instance] for instance in instances])
            print(tabulate(table, tablefmt='simple', headers='firstrow'))
            print("")

    def edit(self):
        """
        Touch the instances file to ensure that it exists.
        """
        # Create the default configuration if none exists
        if not os.path.exists(INSTANCES):

            # Ensure the directory exists
            dirname = os.path.dirname(USERCONFIG)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            # Create and dump an empty instances file
            ManagedInstances().dump()

        # Run the editor
        edit_file(INSTANCES)
