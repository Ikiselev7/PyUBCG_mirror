# -*- coding: utf-8 -*-
"""
    This module instantiate FastTree program to build tree
     of amino acid or nucleotide sequences

"""

import logging
from subprocess import Popen, PIPE

from PyUBCG.abc import AbstractFastTree

LOGGER = logging.getLogger('PyUBCG.fasttree_wrapper')


class FastTree(AbstractFastTree):
    """
        Class-wrapper to run FastTree
    """

    def __init__(self, config):
        self._config = config

    def run(self, file_name, **kwargs) -> None:
        LOGGER.info('Process gene with FastTree. %s output file',
                    kwargs['output_file'])
        args = ['FastTree', '-quiet'] + kwargs['tree_args'] + [file_name]
        proc = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        proc_out, proc_err = proc.communicate()
        if proc_err == '':
            with open(kwargs['output_file'], 'w') as out:
                for line in proc_out:
                    out.write(line)
        else:
            LOGGER.error(proc_err)
            raise ValueError(f'Invalid args for FastTree,\n\t{proc_err}')
