# geonet.config
# Configuration via YAML files with reasonable defaults
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 10:44:34 2018 -0500
#
# ID: config.py [] benjamin@bengfort.com $

"""
Configuration via YAML files with reasonable defaults
"""

##########################################################################
## Imports
##########################################################################

import os
import dotenv

from confire import Configuration, environ_setting


# Important paths
PROJECT  = os.path.normpath(os.path.join(os.path.dirname(__file__), ".."))
FIXTURES = os.path.join(PROJECT, "fixtures")
USERDATA = os.path.expanduser(os.path.join("~", ".geonet"))
USERCONFIG = os.path.join(USERDATA, "config.yml")


##########################################################################
## Helper Functions
##########################################################################

def load_dotenv(path=None):
    """
    Load the .env into the environment if it exists.
    """
    path = path or dotenv.find_dotenv()
    if path:
        dotenv.load_dotenv(path)


# Load the environment before configuring default settings.
load_dotenv()


##########################################################################
## Primary Configuration
##########################################################################

class AWSAccessConfiguration(Configuration):

    aws_owner_id          = environ_setting("AWS_OWNER_ID", required=False, default="")
    aws_access_key_id     = environ_setting("AWS_ACCESS_KEY_ID", required=True)
    aws_secret_access_key = environ_setting("AWS_SECRET_ACCESS_KEY", required=True)
    aws_region            = environ_setting("AWS_REGION", required=True)


class GeoNetConfiguration(Configuration):

    # Search for configuration
    CONF_PATHS = [
        "/etc/geonet.yml", # System configuration
        USERCONFIG,        # User specific config
    ]

    # Default configuration
    debug    = True  # print warnings
    timezone = "UTC" # timezone for datetimes
    regions  = []    # regions to deploy replicas in

    # AWS Access Configuration
    aws = AWSAccessConfiguration()



##########################################################################
## Load settings immediately on import
##########################################################################

settings = GeoNetConfiguration.load()
