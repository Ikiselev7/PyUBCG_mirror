# -*- coding: utf-8 -*-
"""
    This module instantiate prodigal like program to predict protein
    coding gene

"""

# import os
# import subprocess
# import logging

from src.abc_program_wrapper import UtilWrapperABC


class ProdigalABC(UtilWrapperABC):
    """
    Prodigal wrapper class to predict protein coding gene
    """

    def __new__(cls, config):
        tool_type = config.prodigal_like_tool
        if tool_type == 'prodigal':
            # pylint: disable=cyclic-import
            from src.prodigal_wrapper import Prodigal
            # pylint: enable=cyclic-import
            _impl = Prodigal
        return super(ProdigalABC, cls).__new__(_impl)

    def run(self, file_path: str, **kwargs):
        raise NotImplementedError
