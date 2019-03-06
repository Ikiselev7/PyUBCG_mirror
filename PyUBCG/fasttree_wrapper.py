# -*- coding: utf-8 -*-
"""
    This module instantiate FastTree program to build tree
     of amino acid or nucleotide sequences

"""

from subprocess import Popen, PIPE
import logging
import os

from PyUBCG.abc import AbstractFastTree

LOGGER = logging.getLogger('PyUBCG.fasttree_wrapper')


class FastTree(AbstractFastTree):
    """
        Class-wrapper to run FastTree
    """
    def __init__(self, config):
        self._config = config

    def run(self, file_name, **kwargs) -> None:
        proc = Popen(kwargs['tree_args'])

        proc.wait()
