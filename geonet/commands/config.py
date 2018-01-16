# geonet.commands.config
# Shows and manages the current configuration
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 10:43:22 2018 -0500
#
# ID: config.py [] benjamin@bengfort.com $

"""
Shows and manages the current configuration
"""

##########################################################################
## Imports
##########################################################################

import os
import shutil

from commis import Command
from geonet.utils.editor import edit_file
from geonet.config import GeoNetConfiguration
from geonet.config import FIXTURES, USERCONFIG


##########################################################################
## Command Description
##########################################################################

class ConfigCommand(Command):

    name = "config"
    help = "show the current config and environment"
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
        if args.edit:
            self.edit()

        settings = GeoNetConfiguration.load()
        return str(settings)


    def edit(self):
        """
        Opens the default editor to update the user config, creating one with
        the template data if necessary.
        """

        # Create the default configuration if none exists
        if not os.path.exists(USERCONFIG):

            # Ensure the directory exists
            dirname = os.path.dirname(USERCONFIG)
            if not os.path.exists(dirname):
                os.makedirs(dirname)

            # Copy the fixture configuration
            shutil.copy2(
                os.path.join(FIXTURES, "geonet-example-config.yml"),
                USERCONFIG
            )

        # Run the editor
        edit_file(USERCONFIG)
