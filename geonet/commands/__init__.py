# geonet.commands
# Commands for the GeoNet CLI Utility
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 10:42:26 2018 -0500
#
# ID: geonet.commands.py [] benjamin@bengfort.com $

"""
Commands for the GeoNet CLI Utility
"""

##########################################################################
## Imports
##########################################################################

from .config import ConfigCommand
from .status import StatusCommand
from .regions import RegionsCommand


# List of all commands
COMMANDS = [
    ConfigCommand, StatusCommand, RegionsCommand
]
