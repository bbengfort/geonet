# geonet.console
# The primary command line utility for geonet scripts.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 10:37:15 2018 -0500
#
# ID: console.py [] benjamin@bengfort.com $

"""
The primary command line utility for geonet scripts.
"""

##########################################################################
## Imports
##########################################################################

from commis import color
from commis import ConsoleProgram

from geonet.version import get_version
from geonet.commands import COMMANDS


##########################################################################
## Utility Definition
##########################################################################

DESCRIPTION = "manage AWS resources around the world"
EPILOG = "used in Alia geo-replication experiments at UMD"


##########################################################################
## CLI Utility
##########################################################################

class GeoNetUtility(ConsoleProgram):

    description = color.format(DESCRIPTION, color.CYAN)
    epilog = color.format(EPILOG, color.MAGENTA)
    version = color.format("v{}", color.CYAN, get_version())

    @classmethod
    def load(klass, commands=COMMANDS):
        utility = klass()
        for command in commands:
            utility.register(command)
        return utility


##########################################################################
## Run as a module
##########################################################################

def main():
    app = GeoNetUtility.load()
    app.execute()


if __name__ == '__main__':
    main()
