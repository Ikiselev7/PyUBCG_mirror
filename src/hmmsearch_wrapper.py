# -*- coding: utf-8 -*-
"""
    ACB wrapper to hmmsearch-like program

"""
import os
import subprocess
import logging

#pylint: disable=cyclic-import
from src.abc_hmmsearch import HmmsearchABC
#pylint: enable=cyclic-import

LOGGER = logging.getLogger('PyUBCG.hmm_wrapper')

class Hmmsearch(HmmsearchABC):
    """
    Wrapper to hmmsearch
    """
    def __init__(self, config):
        self.config = config
        self._output_path = config.hmmsearch_output
        self._input_path = config.prodigal_output + os.sep + config.pro_prefix
        self._hmm_base = config.hmm_base


    def run(self, file_path: str, **kwargs) -> None:
        """
        Method to execute hmmsearch
        :param path: some file here
        :kwargs: args to run program with
        :return:
        """
        LOGGER.info('Process %s file prodigal.', file_path)
        process = subprocess.Popen(
            ['hmmsearch', '--noali', '--cut_tc', '-o',
             f'{self._output_path}/{file_path}.out', self._hmm_base,
             f'{self._input_path}/{file_path}'])
        process.wait()
