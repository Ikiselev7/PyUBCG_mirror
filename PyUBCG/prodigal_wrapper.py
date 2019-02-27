# -*- coding: utf-8 -*-
"""
    This module instantiate prodigal like program to predict protein
    coding gene

"""

import subprocess
import logging
import os

from PyUBCG.abc import AbstractProdigal

LOGGER = logging.getLogger('PyUBCG.ProdigalWrapper')

class Prodigal(AbstractProdigal):
    """
        Class-wrapper to run prodigal
    """
    def __init__(self, config):
        self._config = config
        self._dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

        self._input_path = os.path.join(*(self._dirpath, config['paths']['fasta_input_folder']))
        self._gene_pro_path = os.path.join(*(self._dirpath,
                                             config['paths']['prodigal_output'],
                                             config['prefixes']['pro_prefix']
                                             ))
        self._gene_nuc_path = os.path.join(*(self._dirpath,
                                             config['paths']['prodigal_output'],
                                             config['prefixes']['nuc_prefix']
                                             ))
        self._translation_table = config['biological']['prodigal_translation_table']


    def run(self, file_name: str, **kwargs) -> None:
        """
        Method to execute Prodigal program with input file. Save  protein
        translations file and nucleotide sequences file to progigal_output/

        :param file_name: input file
        :return:
        """
        LOGGER.info('Process %s file with prodigal.', file_name)
        process = subprocess.Popen(
            ['prodigal', '-i', '%s/%s' % (self._input_path, file_name),
             '-a', os.path.join(self._gene_pro_path, file_name),
             '-d', os.path.join(self._gene_nuc_path, file_name),
             '-q'],
            stdout=subprocess.DEVNULL
        )
        process.wait()
