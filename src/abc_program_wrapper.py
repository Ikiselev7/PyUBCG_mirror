# -*- coding: utf-8 -*-
"""
    ABC program wrapper

"""

import abc
import shutil
import logging

LOGGER = logging.getLogger('PyUBCG.UtilWrapper')

class UtilWrapperABC(abc.ABC):

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
