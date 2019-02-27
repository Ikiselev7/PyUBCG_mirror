# -*- coding: utf-8 -*-
"""
    This module instantiate mafft like program to create multiple
    sequence alignments of amino acid or nucleotide sequences

"""

from subprocess import Popen, PIPE
import logging
import os

from PyUBCG.abc import AbstractMafft

LOGGER = logging.getLogger('PyUBCG.MafftWrapper')


class Mafft(AbstractMafft):
    """
        Class-wrapper to run Mafft
    """
    def __init__(self, config):
        self._config = config
        self._dirpath = \
            os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._input_dir = \
            os.path.join(self._dirpath, config['paths']['bcg_dir'])
        self._output_dir = \
            os.path.join(self._dirpath, config['paths']['mafft_output'])

    def run(self, file_name: str, **kwargs) -> None:
        """
        Method to execute Mafft program.
        :param file_name: input fasta file for Mafft
        :return:
        """
        LOGGER.info('Process %s file with Mafft.', file_name)
        input_file = os.path.join(self._input_dir, file_name)
        output_file = os.path.join(self._output_dir, file_name)
        args = ['mafft', '--quiet', '--thread', '1', input_file]

        proc = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        err = proc.stderr.read()
        if err == '':
            with open(output_file, 'w') as out:
                for line in proc.stdout:
                    out.write(line)
        else:
            LOGGER.error(err)
            raise Exception('Invalid args for mafft')

        proc.wait()
