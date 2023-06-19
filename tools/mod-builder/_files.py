
import logging
import os
import pathlib

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
