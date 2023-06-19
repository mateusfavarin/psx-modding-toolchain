
import logging
import os
import pathlib
import shutil

logger = logging.getLogger(__name__)
def check_file(fname):
    if not os.path.isfile(fname):
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
    """
    message = "Please make sure that no external processes are accessing this file."
    path = pathlib.Path(fname)
    is_successful = True # default
    try:
        path.unlink(fname)
    except Exception as error: # usually existence, permission, or simultaneous access issues
        logger.exception("Cannot delete file: {}".format(fname), exc_info=error.__cause__)
        print(message, "\n")
        is_successful = False

    return is_successful

def create_directory(dirname):
    """
    TODO: Check if parents True produces intended result
    """
    path_dir = pathlib.Path(dirname)
    path_dir.mkdir(exist_ok=True, parents=True)

def delete_directory(dirname):
    message = "Please make sure no external processes are accessing files in this folder."
    path_dir = pathlib.Path(dirname)
    is_successful = True
    try:
        shutil.rmtree(path_dir)
    except Exception as error: # usually existence, permission, or simultaneous access issues
        logger.exception("Cannot delete folder: {}".format(dirname), exc_info=error.__cause__)
        print(message, "\n")
        is_successful = False

    return is_successful    
