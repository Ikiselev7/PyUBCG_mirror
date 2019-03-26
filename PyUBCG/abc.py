# -*- coding: utf-8 -*-
"""
    This module hold all abstract classes.

"""

import abc
import logging
import shutil


SUPPORTED_CONFIG_FORMATS = ['yaml']
LOGGER = logging.getLogger('PyUBCG.abc')

DOCKERIZED_PROGRAMS = ['transdecoder']

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
            from PyUBCG.config_loader_yaml import ConfigLoaderYaml
            _conf = ConfigLoaderYaml
        return super().__new__(_conf)

    def __init__(self, args):
        path = args['config']
        self.config = self.load_config(path, args)

    @abc.abstractmethod
    def load_config(self, path, args):
        """
        Abstract method to implement concrete config creation base on file
        extension
        :param path:
        :param args:
        :return:
        """

    def get_config(self):
        """return config dict"""
        return self.config

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
        if tool.__class__.__name__.lower() not in DOCKERIZED_PROGRAMS:
            if not tool._check_program_exists():
                LOGGER.debug('%s is not installed', cls.__name__)
                raise ValueError('Program %s is not installed' % cls.__name__)
        return tool

    @abc.abstractmethod
    def run(self, file_name: str, *args, **kwargs) -> None:
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
        if self.__class__.__name__ == 'FastTree':
            return shutil.which(self.__class__.__name__) is not None
        return shutil.which(self.__class__.__name__.lower()) is not None


class AbstractHmmsearch(AbstractUtilWrapper):
    """
    Hmmsearch wrapper class
    """

    def __new__(cls, config):
        tool_type = config['tools']['hmmsearch_like_tool']
        if tool_type == 'hmmsearch':
            from PyUBCG.hmmsearch_wrapper import Hmmsearch
            _impl = Hmmsearch
        return super(AbstractHmmsearch, cls).__new__(_impl)

    def run(self, file_name: str, *args, **kwargs):
        raise NotImplementedError


class AbstractProdigal(AbstractUtilWrapper):
    """
    Prodigal wrapper class to predict protein coding gene
    """

    def __new__(cls, config):
        tool_type = config['tools']['prodigal_like_tool']
        # pylint: disable=cyclic-import
        if tool_type == 'prodigal':
            from PyUBCG.prodigal_wrapper import Prodigal
            _impl = Prodigal
        if tool_type == 'transdecoder':
            from PyUBCG.transdecoder_wrapper import Transdecoder
            _impl = Transdecoder
        # pylint: enable=cyclic-import
        return super(AbstractProdigal, cls).__new__(_impl)

    def run(self, file_name: str, *args, **kwargs):
        raise NotImplementedError


class AbstractMafft(AbstractUtilWrapper):
    """
    Mafft wrapper class to create multiple sequence alignments
    of amino acid or nucleotide sequences
    """
    def __new__(cls, config):
        tool_type = config['tools']['mafft_like_tool']
        if tool_type == 'mafft':
            #pylint: disable=cyclic-import
            from PyUBCG.mafft_wrapper import Mafft
            #pylint: enable=cyclic-import
            _impl = Mafft
        else:
            LOGGER.error('Incorrect mafft_like_tool in config')
            raise Exception('Incorrect tool name for align step. '
                            'Try to specify mafft program in config')
        return super(AbstractMafft, cls).__new__(_impl)

    def run(self, file_name: str, *args, **kwargs):
        raise NotImplementedError


class AbstractFastTree(AbstractUtilWrapper):
    """
    Wrapper class to build tree with FastTree
    """
    def __new__(cls, config):
        tool_type = config.tools.align_tool
        if tool_type == 'FastTree':
            #pylint: disable=cyclic-import
            from PyUBCG.fasttree_wrapper import FastTree
            #pylint: enable=cyclic-import
            _impl = FastTree
        else:
            LOGGER.error('Incorrect align_tool in config')
            raise Exception('Incorrect tool name for build tree step. '
                            'Try to specify FastTree program in config')
        return super(AbstractFastTree, cls).__new__(_impl)

    def run(self, file_name: str, **kwargs):
        raise NotImplementedError
