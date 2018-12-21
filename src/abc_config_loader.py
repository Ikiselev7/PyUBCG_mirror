# -*- coding: utf-8 -*-
"""ABC

"""

import abc

SUPPORTED_CONFIG_FORMATS = ['yaml']

class ConfigLoaderABC(abc.ABC):
    """
    ABC class to load config object from file
    """

    def __new__(cls, args):
        config_format = args.config.split('.')[-1]
        if config_format not in SUPPORTED_CONFIG_FORMATS:
            raise ValueError(
                'Config format is not supported. Use one of: {}'.format(
                    ', '.join(SUPPORTED_CONFIG_FORMATS)))
        if config_format == 'yaml':
            from src.config_loader_yaml import ConfigLoaderYaml
            _conf = ConfigLoaderYaml
        return super().__new__(_conf)

    def __init__(self, args):
        path = args.config
        self.load_config(path, args)

    @abc.abstractmethod
    def load_config(self, path, args):
        """
        Abstract method to implement concrete config creation base on file
        extension
        :param path:
        :param args:
        :return:
        """

    def __getattr__(self, item: str):
        if item not in self.config:
            raise KeyError('Value not in config')
        return self.config[item]
