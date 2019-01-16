# -*- coding: utf-8 -*-
"""
    This module instantiate prodigal like program to predict protein
    coding gene

"""

import subprocess
import logging
import os

from src.abc_prodigal import ProdigalABC

LOGGER = logging.getLogger('PyUBCG.ProdigalWrapper')

class Prodigal(ProdigalABC):
    """
        Class-wrapper to run prodigal
    """
    def __init__(self, config):
        self._config = config
        self._project_dir = config.project_folder
        self._input_path = self._project_dir + os.sep + config.fasta_input_folder
        self._output_path = self._project_dir + os.sep + config.prodigal_output
        self._translation_table = config.prodigal_translation_table
        self._nuc_prefix = self._config.nuc_prefix
        self._pro_prefix = self._config.pro_prefix


    def run(self, file_path: str, **kwargs) -> None:
        """
        Method to execute Prodigal program with input file. Save  protein
        translations file and nucleotide sequences file to progigal_output/

        :param file_path: input file
        :return:
        """
        LOGGER.info('Process %s file prodigal.', file_path)
        process = subprocess.Popen(
            ['prodigal', '-i', '%s/%s' % (self._input_path, file_path),
             '-a', '%s/%s/%s' % (self._output_path, self._pro_prefix, file_path),
             '-d', '%s/%s/%s' % (self._output_path, self._nuc_prefix, file_path),
             '-q'])
        process.wait()
