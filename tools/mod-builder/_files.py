
import logging
import os
import pathlib
import shutil

logger = logging.getLogger(__name__)

def get_file_directory(fname = "config.json", folder = "games"):
    """
    Search each parent folder until the fname is found (if found at all)
    Returns the path with the fname

    Assumes exactly one file on path
    Assumes folder exists on path
    TODO: Prompt user to give absolute path
    """
    # message = "No config.json found. Make sure to set this prerequisite file before continuing."
    path_search = pathlib.Path.cwd() # relative to where the script is run

    count_iterations = 0
    while (path_search != path_search.root):
        logger.debug(f"CWD Parent(x{count_iterations}): {path_search}")
        if (path_search / fname).exists():
            return path_search
        for path in (path_search / folder).rglob("*.json"): # hardcoded
            if path.name == fname:
                return path.parent
        path_search = path_search.parent # move up one directory

        count_iterations += 1
        # if count_iterations == 10:
        #     break

    return path_search

def check_file(fname, quiet=False):
    path = pathlib.Path(fname)
    if not path.exists():
        if not quiet:
            logger.error("fname not found: {}".format(fname))
        return False
    return True

def check_files(list_files):
    """
    All files must exist to return True
    """
    for fname in list_files:
        if not check_file(fname):
            logger.error("Missing prerequisite: {}".format(fname))
            return False

    return True

def delete_file(fname):
    """
    Returns bool based on success
    TODO: missing_ok=True only available for python3.8, but exception handles not found
    """
    path = pathlib.Path(fname)
    is_successful = True # default
    try:
        path.unlink(missing_ok=True) # only on python3.8
    except Exception as error: # usually existence, permission, or simultaneous access issues
        logger.exception("Cannot delete file: {}".format(fname), exc_info=error.__cause__)
        is_successful = False

    return is_successful

def create_directory(dirname):
    """
    TODO: Check if parents True produces intended result
    """
    path_dir = pathlib.Path(dirname)
    path_dir.mkdir(exist_ok=True, parents=True)

def delete_directory(dirname):
    path_dir = pathlib.Path(dirname)
    is_successful = True
    try:
        shutil.rmtree(path_dir, ignore_errors=True)
    except Exception as error: # usually existence, permission, or simultaneous access issues
        logger.exception("Cannot delete folder: {}".format(dirname), exc_info=error.__cause__)
        is_successful = False

    return is_successful
