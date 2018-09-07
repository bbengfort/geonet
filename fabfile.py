# fabfile
# Systems administration for running hosts.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Fri Aug 10 09:30:54 2018 -0400
#
# ID: fabfile.py [] benjamin@bengfort.com $

"""
Systems administration for running hosts.
"""

##########################################################################
## Imports
##########################################################################

import os

from tabulate import tabulate
from functools import partial
from collections import Counter
from geonet.utils import load_ssh_config
from dotenv import load_dotenv, find_dotenv

from fabric.api import parallel, task, runs_once, execute
from fabric.api import env, run, cd, get, put, hide, sudo, settings


##########################################################################
## Environment
##########################################################################

## Load the environment
load_dotenv(find_dotenv())

## Local Paths
SSH_CONFIG = os.path.expanduser("~/.ssh/geonet.config")

## Remote Paths
GOPATH = "~/workspace/go"
GOINSTALL = "/usr/local/go"

## Fabric ENV
env.user = "ubuntu"
env.ssh_config_path = SSH_CONFIG
env.hosts = sorted(list(load_ssh_config(SSH_CONFIG).keys()))
env.colorize_errors = True
env.use_ssh_config = True
env.forward_agent = True


##########################################################################
## Fabric Commands
##########################################################################

@task
@runs_once
def go_version():
    """
    Prints out the currently installed Go version on all hosts.
    """

    @parallel
    def fetch_go_version():
        return run("go version")

    with hide("output", "running"):
        data = execute(fetch_go_version)

    n_hosts = float(len(data))
    versions = Counter(data.values())

    table = [["Version", "Replicas", "Percent"]]
    for version, count in versions.most_common():
        table.append([version, count, float(count) / n_hosts * 100])

    print(tabulate(table))


@task
@parallel
def update():
    """
    Runs apt-get autoremove, update, and upgrade for Ubuntu maintenance
    """
    # with hide("output"):
    sudo("apt-get update -qy")
    sudo("apt-get upgrade -qy --autoremove")


@task
@parallel
def reboot():
    """
    Reboot the instances to start fresh and let settings take effect
    """
    with settings(warn_only=True):
        sudo("reboot")


@task
@parallel
def reset_dpkg():
    """
    If update is interrupted, reset dpkg to correct the problem
    """
    sudo("dpkg --configure -a")


@task
@parallel
def install_ats_chrony():
    """
    Install Amazon Time Service with chrony
    """
    # Install Chrony
    sudo("apt install chrony -y")

    # Update the configuration to use the amazon time server
    conf = os.path.join(os.path.dirname(__file__), "fixtures", "chrony.conf")
    put(conf, "/etc/chrony/chrony.conf", use_sudo=True)

    # Restart the time service
    sudo("/etc/init.d/chrony restart")



##########################################################################
## Helper Functions
##########################################################################

# Add default arguments to tabulate
tabulate = partial(tabulate, headers='firstrow', tablefmt='simple')
