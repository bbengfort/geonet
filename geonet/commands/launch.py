# geonet.commands.launch
# Launch instances using the specified template.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Mon Jan 22 22:58:36 2018 -0500
#
# ID: launch.py [] benjamin@bengfort.com $

"""
Launch instances using the specified template.
"""

##########################################################################
## Imports
##########################################################################

from commis import color
from commis import Command
from functools import partial

from geonet.ec2 import Instances
from geonet.region import Regions
from geonet.config import settings
from geonet.utils.async import wait
from geonet.managed import ManagedInstances


INSTANCE_TYPES = (
    't2.nano', 't2.micro', 't2.small', 't2.medium',
    't2.large', 't2.xlarge', 't2.2xlarge'
)

##########################################################################
## Luanch Command
##########################################################################

class LaunchCommand(Command):

    name = "launch"
    help = "launch instances using the alia template"
    args = {
        ('-r', '--regions'): {
            'choices': settings.regions, 'default': settings.regions,
            'metavar': 'REGION', 'nargs': "*",
            'help': 'specify regions to get the status for',
        },
        ('-t', '--type'): {
            'choices': INSTANCE_TYPES, 'default': settings.instance_type,
            'help': 'specify the instance type to launch',
        },
        ('-s', '--start_index'): {
            'type': int, 'default': 1, 'metavar': 'N',
            'help': 'index to start instance numbering at',
        },
        "N": {
            'type': int, 'help': 'number of instances to launch per region',
        }
    }

    def handle(self, args):
        """
        Handle the launch command
        """

        # Load the regions for the launch command
        regions = Regions(
            region for region in Regions.load()
            if str(region) in args.regions
        )

        # Get the templates associated with each region
        self.templates = regions.launch_templates()

        # Launch the instances with the specified template
        instances = Instances.collect(wait(
            (partial(self.launch_in_region, region) for region in regions),
            args=(args,)
        ))

        # Rename the instances given
        wait((
            partial(self.tag_instance, instance, idx)
            for idx, instance in enumerate(instances)
        ), args=(args,))

        # Update the instances under management
        manager = ManagedInstances.load()
        for instance in instances:
            manager.add(str(instance), instance.region)
        manager.dump()

        # Report what went down
        print(color.format(
            "created {} instances in {} regions",
            color.LIGHT_GREEN, len(instances), len(regions)
        ))


    def launch_in_region(self, region, args):
        """
        Launch the specified number of replicas in the given region
        """
        template = self.templates.get_alia_template(region)
        kwargs = {
            "InstanceType": args.type,
            "MaxCount": args.N,
            "MinCount": args.N,
            "LaunchTemplate": {
                "LaunchTemplateId": str(template),
            },
        }
        resp = region.conn.run_instances(**kwargs)
        return Instances(resp['Instances'], region=region)

    def tag_instance(self, instance, idx, args):
        """
        Give the instance a unique name
        """
        name = "alia-{}-{}".format(
            instance.region.name.lower().replace(" ", "-"),
            idx + args.start_index
        )

        instance.region.conn.create_tags(
            Resources=[str(instance)], Tags= [
                {'Key': 'Name', 'Value': name},
            ]
        )
