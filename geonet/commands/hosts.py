# geonet.commands.hosts
# Creates a host file for instances currently running.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Fri Feb 02 14:47:34 2018 -0500
#
# ID: hosts.py [] benjamin@bengfort.com $

"""
Creates a host file for instances currently running.
"""

##########################################################################
## Imports
##########################################################################

import os
import sys
import json

from commis import Command
from collections import defaultdict
from contextlib import contextmanager

from geonet.managed import ManagedInstances


##########################################################################
## Hosts Command
##########################################################################

class HostsCommand(Command):

    name = "hosts"
    help = "get the SSH host information for running instances"
    args = {
        ('-o', '--outpath'): {
            'default': None, 'metavar': 'PATH',
            'help': 'path to write out host information'
        },
        ('-f', '--format'): {
            'choices': ('config', 'json'), 'default': 'config',
            'help': 'specify the output format of the hosts'
        },
        ('-i', '--ipaddr'): {
            'action': 'store_true', 'default': False,
            'help': 'use IP address instead of hostname for SSH',
        },
        ('-u', '--user'): {
            'default': 'ubuntu', 'help': 'default SSH user to connect with'
        },
        ('-p', '--port'): {
            'type': int, 'default': 22,
            'help': 'default SSH port to connect with',
        },
        ('-s', '--ssh-dir') : {
            'default': '~/.ssh', 'metavar': 'PATH',
            'help': 'location of SSH configuration and key files',
        },
        '--no-forward-agent': {
            'action': 'store_true', 'default': False,
            'help': 'do not add forward agent configuration'
        },
    }

    def handle(self, args):
        """
        Handle the hosts commands and command line arguments
        """
        # Load the instance manager and get instance information
        manager = ManagedInstances.load()

        # Default host data
        defaults = {
            'user': args.user,
            'port': args.port,
            'forward_agent': False if args.no_forward_agent else True
        }

        # Get the SSH information for each instance
        hosts = defaultdict(lambda: defaults.copy())
        for instance in manager.status():
            host = hosts[instance.name]
            host["hostname"] = instance.ipaddr if args.ipaddr else instance.hostname
            host["key"] = os.path.join(args.ssh_dir, "{}.pem".format(instance["KeyName"]))

        # Write out the data to the outpath
        if args.format == 'json':
            self.write_json(hosts, args.outpath)

        elif args.format == 'config':
            self.write_config(hosts, args.outpath)

        else:
            raise ValueError("unknown hosts format '{}'".format(args.format))

    def write_json(self, hosts, outpath):
        """
        Write JSON hosts to specified otuput
        """
        with self.open(outpath) as f:
            json.dump(hosts, f, indent=2)

    def write_config(self, hosts, outpath):
        """
        Write SSH config file data to specified output
        """
        with self.open(outpath) as f:
            for host, info in hosts.items():
                output = (
                    "Host {host}\n"
                    "    HostName {hostname}\n"
                    "    User {user}\n"
                    "    Port {port}\n"
                    "    IdentityFile {key}\n"
                    "    ForwardAgent {forward_agent}\n\n"
                )
                f.write(output.format(host=host, **info))

    @contextmanager
    def open(self, outpath):
        if outpath is None:
            yield sys.stdout
        else:
            with open(outpath, 'w') as f:
                yield f
