
import logging
import os
import pathlib

logger = logging.getLogger(__name__)
def check_file(fname):
    if not os.path.isfile(fname):
        logger.error("fname not found: {}".format(fname))
        return False
    return True
