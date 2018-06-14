# -*- coding: utf-8 -*-
# geonet.commands.kahu
# CLI Interactions with the Kahu API
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Thu Jun 14 07:20:32 2018 -0400
#
# ID: kahu.py [] benjamin@bengfort.com $

"""
CLI Interactions with the Kahu API
"""

##########################################################################
## Imports
##########################################################################

import boto3

from commis import color
from commis import Command
from tabulate import tabulate

from geonet.kahu import Kahu
from geonet.managed import ManagedInstances

CHECKMARK  = color.format(u"✓", color.LIGHT_GREEN)
CROSSMARK  = color.format(u"✗", color.LIGHT_RED)


##########################################################################
## List Command
##########################################################################

class KahuStatusCommand(Command):

    name = "kahu"
    help = "report the Kahu service status and version"
    args = {}

    def handle(self, args):
        kahu = Kahu()
        status = kahu.status()
        table = [["service", kahu.base_url]] + [[key, value] for key, value in status.items()]
        print(tabulate(table, tablefmt="plain"))


class KahuListCommand(Command):

    name = "kahu:list"
    help = "list the active replicas in Kahu"
    args = {}

    def handle(self, args):
        kahu = Kahu()
        replicas = kahu.replicas()

        table = [["PID", "Name", "IP Address", "Domain", "Port"]]
        for replica in replicas:
            table.append([
                replica["pid"], replica["name"], replica["ipaddr"], replica["domain"], replica["port"]
            ])

        print(tabulate(table, tablefmt="simple", headers="firstrow"))


class KahuCreateReplicaCommand(Command):

    name = "kahu:create"
    help = "create a Kahu replica from an AWS instance"
    args = {
        ("-A", "--all"): {
            "action": "store_true", "default": False,
            "help": "create replicas for all managed instances",
        },
        "instance_id": {
            "nargs": "*",
            "help": "the instance ids to create replicas for"
        }
    }

    def handle(self, args):
        self.instances = ManagedInstances.load()
        instance_ids = list(self.instances) if args.all else args.instance_id

        if len(instance_ids) == 0:
            print(color.format("no instances to create", color.YELLOW))

        results = [
            self.handle_instance_id(iid, args) for iid in instance_ids
        ]

        print(tabulate(results, tablefmt="simple", headers="keys"))


    def handle_instance_id(self, instance_id, args):
        # Compose response for results table
        response = {"instance_id": instance_id, "created": CROSSMARK, "message": ""}

        # Only allow managed instances to be created
        if instance_id not in self.instances:
            response["message"] = "{} is not a managed instance".format(instance_id)
            return response

        # Lookup the region the instance is associated with
        region = self.instances.get_region_for_instance(instance_id)
        if region is None:
            response["message"] = "could not determine region for {}".format(instance_id)
            return response

        # Look up instance details
        ec2 = boto3.resource('ec2', region_name=str(region))
        instance = ec2.Instance(instance_id)

        try:
            instance.load()
        except Exception as e:
            response["message"] = str(e).split(":")[-1].strip()
            return response

        # Can only create instances that are running
        if instance.state["Name"] != "running":
            response["message"] = "can only create replicas for running instances (Public IP)"
            return response

        # Determine instance name from tag
        name = None
        for tag in instance.tags:
            if tag["Key"].lower() == "name":
                name = tag["Value"]
                break
        else:
            response["message"] = "could not look up name from tags"
            return response

        if not name.startswith("alia"):
            response["message"] = "{} is not an alia host?".format(name)
            return response

        try:
            pid = int(name.split("-")[-1])
        except ValueError:
            response["message"] = "could not parse pid from {}".format(name)
            return response

        description = "AWS {} instance ({}) running in {} ({}).".format(
            instance.instance_type, instance.instance_id, region.name,
            instance.placement["AvailabilityZone"],
        )

        # Create a Kahu Replica from the instance
        replica = {
            "pid": pid,
            "name": name,
            "hostname": instance.private_dns_name.split(".")[0],
            "ipaddr": instance.public_ip_address,
            "domain": instance.public_dns_name,
            "description": description,
            "aws_instance": {
                "instance_id": instance.instance_id,
                "instance_type": instance.instance_type,
                "availability_zone": instance.placement["AvailabilityZone"],
            }
        }

        kahu = Kahu()
        res, success = kahu.create_replica(replica)
        if success:
            response["created"] = CHECKMARK
            response["message"] = "{} created!".format(name)
        else:
            response["message"] = "400 bad request from Kahu (duplicate)"

        return response
