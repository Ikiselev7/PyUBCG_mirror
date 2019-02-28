"""Module with utils"""

import os
import logging

from trafaret_config import ConfigError, read_and_validate

from PyUBCG.validators import CONFIG_SCHEMA

LOGGER = logging.getLogger('PyUBCG.read_config')


def read_config(filepath):
    """Read a config file from a given path"""
    try:
        config = read_and_validate(filepath, CONFIG_SCHEMA)
        return config
    except ConfigError as ex:
        ex.output()
        raise

def read_config_from_path(config):
    """Read config from a file path in"""
    dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    filepath = os.path.join(dirpath, config)
    if not os.path.isfile(filepath):
        LOGGER.error("Passed config does not exist: %s", config)
        return None
    return read_config(filepath)
