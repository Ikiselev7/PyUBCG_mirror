# -*- coding: utf-8 -*-
"""
    yaml config loader

"""

import yaml
#pylint: disable=cyclic-import
from PyUBCG.abc_config_loader import ConfigLoaderABC
#pylint: enable=cyclic-import

class ConfigLoaderYaml(ConfigLoaderABC):
    """
    Class to load config object from .yaml file
    """
    def load_config(self, path: str, args):
        """
        Method to load config from .yaml file
        :param path: path to config
        :param args: Namespace with args from commandline
        :return: config object
        """
        with open(path) as yaml_conf:
            self.config = yaml.load(yaml_conf)
        for key, value in args.items():
            self.config[key] = value
