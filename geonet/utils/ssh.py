# geonet.utils.ssh
# Helpers for handling SSH configuration files.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created:
#
# ID: geonet.utils.ssh.py [] benjamin@bengfort.com $

"""
Helpers for handling SSH configuration files.
"""

##########################################################################
## Imports
##########################################################################

from collections import defaultdict

##########################################################################
## Utility Functions
##########################################################################

def load_ssh_config(path):
    hosts = defaultdict(dict)
    host = None

    with open(path, 'r') as f:
        for line in f:
            # Skip comments and empty lines
            line = line.strip()
            if not line or line.startswith("#"):
                continue

            # Get key/value pair
            parts = line.split()
            key, value = parts[0], " ".join(parts[1:])

            # Check if we're a host
            if key.lower() == "host":
                host = value
                continue

            # Add key/value to config
            hosts[host][key] = value

    return hosts


if __name__ == '__main__':
    import os
    import json
    print(json.dumps(load_ssh_config(os.path.expanduser("~/.ssh/geonet.config")), indent=2))
