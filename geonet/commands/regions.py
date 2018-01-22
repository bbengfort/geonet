# -*- coding: utf-8 -*-
# geonet.commands.regions
# Gets information about the regions currently configured.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 21:38:08 2018 -0500
#
# ID: regions.py [] benjamin@bengfort.com $

"""
Gets information about the regions currently configured.
"""

##########################################################################
## Imports
##########################################################################

import os

from commis import color
from commis import Command
from tabulate import tabulate
from geonet.ec2 import connect, Instance
from geonet.utils.editor import edit_file
from geonet.utils.serialize import to_json
from geonet.region import Regions, REGIONDATA


CHECKMARK = color.format(u"✓", color.LIGHT_GREEN)


##########################################################################
## Command Description
##########################################################################

class RegionsCommand(Command):

    name = "regions"
    help = "describe configured regions"
    args = {
        ('-e', '--edit'): {
            'action': 'store_true', 'help': 'edit region locale names',
        },
        ('-d', '--data'): {
            'action': 'store_true', 'help': 'print region data path and exit',
        },
        ('-K', '--key-pairs'): {
            'action': 'store_true', 'help': 'count available key pairs',
        },
        ('-T', '--launch-templates'): {
            'action': 'store_true', 'help': 'count available launch templates',
        },
        ('-I', '--images'): {
            'action': 'store_true', 'help': 'count available AMIs',
        },
        ('-G', '--security-groups'): {
            'action': 'store_true', 'help': 'count available security groups',
        },
        ('-S', '--state'): {
            'choices': (
                'all', Instance.PENDING, Instance.RUNNING, Instance.STOPPED,
                Instance.SHUTTING_DOWN, Instance.STOPPING, Instance.TERMINATED
            ),
            'nargs': '*', 'default': [],
            'help': 'count instances with specified state (can specify multiple)',
        },
        ('-f', '--format'): {
            'choices': ('plain', 'simple', 'pipe', 'psql', 'html', 'latex', 'json'),
            'default': 'simple',
            'help': 'format to display the regions table in',
        },
    }

    def handle(self, args):
        """
        Handles the regions command with arguments from the command line.
        """
        # Print path to region data and exit
        if args.data:
            print(REGIONDATA)
            return

        # Load or fetch regions
        regions = self.fetch(args)
        regions.sortby('RegionName')

        # Edit locale names of regions
        if args.edit:
            edit_file(REGIONDATA)

        # Create the report with all additional data
        report, headers = self.report(regions, args)

        # Print command line readable representation
        self.pprint(report, headers, args)

    def fetch(self, args):
        """
        Loads the regions from disk unless they don't exist or the user asks
        for them to be updated, then fetches them with boto.
        """
        # TODO: provide update functionality
        if not os.path.exists(REGIONDATA):
            regions = Regions.fetch(connect())
            regions.dump()
            return regions

        return Regions.load()

    def report(self, regions, args):
        """
        Create the region report dataset to print or serialize.
        """
        # TODO: parallelize reporting

        # Create default data set
        headers = ['Used', 'Name', 'Region']
        data = [{
            'Used': r.is_configured(),
            'Name': r.locale,
            'Region': str(r),
        } for r in regions]

        # Add additional data
        for idx, item in enumerate(data):
            region = regions[idx]

            # Add key pairs count if requested
            if args.key_pairs:
                item['Keys'] = len(region.key_pairs())
                if idx == 0: headers.append('Keys')

            # Add launch templates if requested
            if args.launch_templates:
                item['Templates'] = len(region.launch_templates())
                if idx == 0: headers.append('Templates')

            # Add images if requested
            if args.images:
                item['AMIs'] = len(region.images())
                if idx == 0: headers.append('AMIs')

            # Add security groups if requested
            if args.security_groups:
                item['SGs'] = len(region.security_groups())
                if idx == 0: headers.append('SGs')

            # Add instance counts to the report
            if args.state:
                instances = region.instances()
                for state in args.state:
                    if state == 'all':
                        item['Instances'] = len(instances)
                        if idx ==0: headers.append('Instances')
                    else:
                        item[state.title()] = sum(
                            1 for _ in instances.with_states(state)
                        )
                        if idx ==0: headers.append(state.title())

        return data, headers

    def pprint(self, report, headers, args):
        """
        Pretty print the regions data for the command line.
        """

        # Data serialization
        if args.format == 'json':
            print(to_json(report, indent=2))
            return

        # Make human readable
        for item in report:
            item['Used'] = CHECKMARK if item['Used'] else ""

        # Tabulate the report and print
        table = [headers]
        table += [
            [row[key] for key in headers]
            for row in report
        ]

        print(tabulate(table, tablefmt=args.format, headers='firstrow'))
