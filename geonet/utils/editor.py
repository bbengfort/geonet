# geonet.utils.editor
# Wrapper for a command line editor to edit files.
#
# Author:  Benjamin Bengfort <benjamin@bengfort.com>
# Created: Tue Jan 16 11:43:40 2018 -0500
#
# ID: editor.py [] benjamin@bengfort.com $

"""
Wrapper for a command line editor to edit files.
"""

##########################################################################
## Imports
##########################################################################

import os
import shutil
import tempfile
import subprocess


##########################################################################
## Module Constants
##########################################################################

EDITOR_ENVVAR = "EDITOR"
EDITOR_SEARCH = ["vim", "emacs", "nano"]


##########################################################################
## Editor functionality
##########################################################################

def edit_file(path, editor=None):
    """
    Edit the file at the specified path using a command line editor
    """

    # Find the editor to use
    editor = find_editor(editor)

    # Create temporary directory and copy the file
    tmpdir = tempfile.mkdtemp()
    tmpfile = os.path.join(tmpdir, os.path.basename(path))
    shutil.copy2(path, tmpfile)

    # Execute the editor
    subprocess.call([editor, tmpfile])

    # Copy the temporary file back and cleanup
    shutil.copy2(tmpfile, path)
    shutil.rmtree(tmpdir)


def find_editor(name=None):
    """
    Finds the path to the specified editor name, looks up the editor name in
    the enivornment or uses the editor search to find the path to an editor.
    Raises an exception if the editor could not be found.
    """

    def is_exe(fpath):
        return os.path.isfile(fpath) and os.access(fpath, os.X_OK)

    def search(fname):
        for path in os.getenv("PATH").split(os.pathsep):
            fpath = os.path.join(path, fname)
            if is_exe(fpath):
                return fpath

    # Find name or lookup in the environment
    name = name or os.getenv(EDITOR_ENVVAR)
    if name is not None:
        fpath, fname = os.path.split(name)
        if fpath and is_exe(name):
            return name
        else:
            fpath = search(fname)
            if fpath is not None:
                return fpath

        # Could not look up name at this point
        raise ValueError("could not find editor path {}".format(name))

    # Perform search for editors
    for name in EDITOR_SEARCH:
        fpath = search(name)
        if fpath is not None:
            return fpath

    # Could not find any editors at all
    raise LookupError("could not find an editor")
