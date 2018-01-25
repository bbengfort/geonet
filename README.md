# GeoNet

**Helper python scripts for managing AWS resources around the world**

A helper library for managing experiments across a globally distributed  network of replicas hosted on AWS. These tools use command line scripts,  configuration files and Boto to meaningfully interact with AWS for the  purpose of monitoring replicas, resources, and experiments.

## Getting Started

This library has been built for experimental purposes and as a result is not largely tested. Please report any bugs on [GitHub issues](https://github.com/bbengfort/geonet/issues). To install the software, first clone the repository then install the package in editable mode as follows:

    $ git clone https://github.com/bbengfort/geonet.git
    $ cd geonet
    $ pip install -e .

This should install all of the requirements found in the `requirements.txt` file. If it doesn't or to install additional testing requirements for development, install dependencies as follows:

    $ pip install -r requirements.txt
    $ pip install -r tests/requirements.txt

After installing the package in _editable_ mode (e.g. `pip install -e`), the `geonet` command should be on your path. The first thing to do is setup your configuration as follows:

    $ geonet config -e

This will open an editor, allowing you to manage your configuration and will also tell you what environment variables to set. If an error occurs because an editor cannot be found, or to change the default editor used set the `$EDITOR` environment variable with the path to your editor of choice. Note that your editor must remain in the foreground process otherwise this will fail (e.g. don't use a GUI editor).

The next step is to get a complete report about regions:

    $ geonet regions -GTKI -S all

Use `geonet regions --help` to see the available reporting commands. Note this could take a while as it will be querying AWS multiple times. This will print out a region report that lists the current state of your environment. You can activate regions for the rest of the app by using `geonet config -e` and you can set locale names (e.g. set `"US West 2"` to `"Oregon"`) by using `geonet regions -e`, which will allow you to edit the JSON description of the regions directly.

Once you have activated the regions required for your experiment, you can start to create key pairs, security groups, and AMIs. Currently this is not supported from the command line, but will be soon. Ensure that you create these resources named with an `alia-` prefix so the app can find it. You can describe resources as follows:

    $ geonet descr keys
    $ geonet descr groups
    $ geonet descr images

Once these items have been created, create launch templates in each region as follows:

    $ geonet template

Note this command requires the alia prefixed keys, groups, and images and can only be run once. Soon this command will allow the creation of versioned templates.

## Managing Instances

Instances "under management" are instances that are specifically inspected in the `start`, `stop`, and `status` commands. They are created by the `launch` command and deleted with the `destroy` command, though you can manually edit the instances under management by using `geonet list -e`.

Launching instances uses the template created in the previous step. To launch N instances in each region:

    $ geonet launch N

All instances launched will be added to the managed instances as well as renamed with an index and the location to ensure they are understandable. Once launched, inspect the status of instances with:

    $ geonet status

Finally you can use the `geonet stop` and `geonet start` commands to start and stop the instances on demand. Note, you'll be charged for running instances as well as any EBS volumes created!

To destroy instances use the `geonet destroy` command, which terminates instances and then removes them from being under management. 
