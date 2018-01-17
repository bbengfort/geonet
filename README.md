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

Once you have activated the regions required for your experiment, you can start to create key pairs, security groups, launch templates, etc. with the various commands (if they're not set up already).
