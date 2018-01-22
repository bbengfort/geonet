# geonet.commands.template
# Create and manage launch templates
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 14:05:28 2018 -0500
#
# ID: template.py [] benjamin@bengfort.com $

"""
Create and manage launch templates
"""

##########################################################################
## Imports
##########################################################################

from commis import Command
from geonet.region import Regions
from geonet.utils.async import wait

from functools import partial


##########################################################################
## Command Description
##########################################################################

class TemplateCommand(Command):

    name = "template"
    help = "create and manage launch templates"
    args = {}

    def handle(self, args):
        """
        Handle the template command
        """
        regions = Regions.load_active()
        wait((partial(self.handle_region, region) for region in regions), args=(args,))

    def handle_region(self, region, args):
        """
        Handles each individual region template creation request.
        """

        groups = region.security_groups().get_alia_groups()
        amis = region.images().sort_latest().get_alia_images()
        keys = region.key_pairs().get_alia_keys()

        if len(groups) != 1:
            raise ValueError("not enough or too many security groups")

        if len(amis) == 0:
            raise ValueError("no latest AMI to build template from")

        if len(keys) != 1:
            raise ValueError("not enough or too many key pairs")

        data = {
            'ImageId': str(amis[0]),
            'InstanceType': 't2.micro',
            'KeyName': str(keys[0]),
            'Monitoring': {'Enabled': False},
            'DisableApiTermination': False,
            'InstanceInitiatedShutdownBehavior': 'terminate',
            'TagSpecifications': [
                {
                    'ResourceType': 'instance',
                    'Tags': [
                        {
                            'Key': 'Service',
                            'Value': 'Alia'
                        },
                        {
                            'Key': 'Roles',
                            'Value': 'Replica, Workload'
                        },
                    ],
                },
                {
                    'ResourceType': 'volume',
                    'Tags': [
                        {
                            'Key': 'Role',
                            'Value': 'Alia Temporary Data'
                        },
                    ],
                },
            ],
            'SecurityGroupIds': [str(groups[0])],
        }

        region.conn.create_launch_template(
            LaunchTemplateName='alia',
            VersionDescription="alia image '{}' launch template".format(amis[0].name),
            LaunchTemplateData=data
        )
