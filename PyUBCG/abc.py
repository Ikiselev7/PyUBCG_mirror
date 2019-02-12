# -*- coding: utf-8 -*-
"""
    This module hold all abstract classes.

"""

import abc
import logging
import shutil


SUPPORTED_CONFIG_FORMATS = ['yaml']
LOGGER = logging.getLogger('PyUBCG.abc')


class AbstractConfigLoader(abc.ABC):
    """
    ABC class to load config object from file
    """
    LOGGER = logging.getLogger('PyUBCG.config_loader_yaml')

    def __new__(cls, args):
        config_format = args['config'].split('.')[-1]
        if config_format not in SUPPORTED_CONFIG_FORMATS:
            raise ValueError(
                'Config format is not supported. Use one of: {}'.format(
                    ', '.join(SUPPORTED_CONFIG_FORMATS)))
        if config_format == 'yaml':
            from PyUBCG.config_loader_yaml import AbstractConfigLoaderYaml
            _conf = AbstractConfigLoaderYaml
        return super().__new__(_conf)

    def __init__(self, args):
        path = args['config']
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
            LOGGER.error('Value %s not in config', item)
            return None
        return self.config[item]


class AbstractUtilWrapper(abc.ABC):

    """
    ABC class to implement wrapper class to program
    """

    def __new__(cls):
        """
        Adjust method to check presence of program in system
        :param args:
        :param kwargs:
        :return: Wrapper object
        """
        tool = super().__new__(cls)
        # pylint: disable=W0212
        if not tool._check_program_exists():
            LOGGER.debug('%s is not installed', cls.__name__)
            raise ValueError('Program %s is not installed' % cls.__name__)
        return tool

    @abc.abstractmethod
    def run(self, file_path: str, **kwargs) -> None:
        """
        abstract method to be implemented in progeny classes
        :param path: path to some file
        :return:
        :kwargs: args to run program
        """

    def _check_program_exists(self) -> bool:
        """
        Method to check presence of program in system
        :param name: program name
        :return:
        """
        return shutil.which(self.__class__.__name__.lower()) is not None


class AbstractHmmsearch(AbstractUtilWrapper):
    """
    Hmmsearch wrapper class
    """

    def __new__(cls, config):
        tool_type = config.hmmsearch_like_tool
        if tool_type == 'hmmsearch':
            from PyUBCG.hmmsearch_wrapper import Hmmsearch
            _impl = Hmmsearch
        return super(AbstractHmmsearch, cls).__new__(_impl)

    def run(self, file_path: str, **kwargs):
        raise NotImplementedError


class AbstractProdigal(AbstractUtilWrapper):
    """
    Prodigal wrapper class to predict protein coding gene
    """

    def __new__(cls, config):
        tool_type = config.prodigal_like_tool
        if tool_type == 'prodigal':
            # pylint: disable=cyclic-import
            from PyUBCG.prodigal_wrapper import Prodigal
            # pylint: enable=cyclic-import
            _impl = Prodigal
        return super(AbstractProdigal, cls).__new__(_impl)

    def run(self, file_path: str, **kwargs):
        raise NotImplementedError
