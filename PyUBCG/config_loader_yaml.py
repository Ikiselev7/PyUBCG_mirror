# -*- coding: utf-8 -*-
"""
    yaml config loader

"""

#pylint: disable=cyclic-import
from PyUBCG.abc import AbstractConfigLoader
from PyUBCG.utils import read_config_from_path
#pylint: enable=cyclic-import

class ConfigLoaderYaml(AbstractConfigLoader):
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
        add_config = {}
        config = read_config_from_path(path)
        for key, value in args.items():
            #  we iterate over config from file to pass values from
            #  console call
            if value is not None:
                for sub_dict in config:
                    for parameter in config[sub_dict]:
                        if parameter == key:
                            config[sub_dict][parameter] = value
                            continue
            #  this for rest possible values that we have got from
            #  cli that are not in config yet or not intended
            #  to be there like input_file
            add_config[key] = value
        new_config = {**config, **add_config}
        return new_config
