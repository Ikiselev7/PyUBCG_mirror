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
        self._input_folder = os.path.join(
            self._dirpath,
            self._config.paths.align_input_parse,
            self._config.prefixes.align_prefix
        )
        self._output_folder = os.path.join(
            self._dirpath,
            self._config.paths.align_mafft_output,
            self._config.prefixes.align_prefix
        )
        if self._config.align_mode == 'nt':
            self._input_postfix = self._config.postfixes.input_parsing_dna_const
            self._output_postfix = self._config.postfixes.mafft_res_pro_const
        else:
            self._input_postfix = self._config.postfixes.input_parsing_pro_const
            self._output_postfix = self._config.postfixes.mafft_res_dna_const


    def run(self, gene_name: str, *args, **kwargs) -> tuple:
        """
        Method to execute Mafft program.
        Accept
        :param file_name: input fasta file for Mafft
        :return:
        """
        input_file = os.path.join(self._input_folder,
                                  gene_name + self._input_postfix)
        output_file = os.path.join(self._output_folder,
                                   gene_name+self._output_postfix)
        LOGGER.info('Process %s gene with Mafft. %s output file', gene_name, output_file)
        args = ['mafft', '--quiet', '--thread', str(self._config.general.processes),
                input_file]
        proc = Popen(args, stdout=PIPE, stderr=PIPE, universal_newlines=True)
        err = proc.stderr.read()
        if err == '':
            with open(output_file, 'w') as out:
                for line in proc.stdout:
                    out.write(line)
        else:
            LOGGER.error(err)
            raise ValueError(f'Invalid args for mafft,\n\t{err}')
        proc.wait()
        return output_file, gene_name

