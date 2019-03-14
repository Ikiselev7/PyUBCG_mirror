# -*- coding: utf-8 -*-
"""
    This module instantiate FastTree program to build tree
     of amino acid or nucleotide sequences

"""

from subprocess import Popen, PIPE
import logging


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
        err = proc.stderr.read()
        if err == '':
            with open(kwargs['output_file'], 'w') as out:
                for line in proc.stdout:
                    out.write(line)
        else:
            LOGGER.error(err)
            raise ValueError(f'Invalid args for FastTree,\n\t{err}')
        proc.wait()
