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
from .descr import DescribeCommand
from .template import TemplateCommand
from .launch import LaunchCommand
from .list import ListCommand
from .stop import StopCommand
from .start import StartCommand
from .destroy import DestroyCommand
from .hosts import HostsCommand
from .sgs import SecurityGroupCreateCommand
from .sgs import SecurityGroupAuthCommand
from .sgs import SecurityGroupDestroyCommand
from .sgs import SecurityGroupRevokeCommand
from .kahu import KahuStatusCommand
from .kahu import KahuListCommand
from .kahu import KahuCreateReplicaCommand


# List of all commands
COMMANDS = [
    ConfigCommand, StatusCommand, RegionsCommand, DescribeCommand,
    TemplateCommand, LaunchCommand, ListCommand, StopCommand, StartCommand,
    DestroyCommand, HostsCommand, SecurityGroupCreateCommand,
    SecurityGroupDestroyCommand, SecurityGroupAuthCommand,
    SecurityGroupRevokeCommand, KahuStatusCommand, KahuListCommand,
    KahuCreateReplicaCommand, 
]
