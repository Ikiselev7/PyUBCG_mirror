# -*- coding: utf-8 -*-
"""
    ACB wrapper to hmmsearch-like program

"""
import os
import subprocess
import logging

#pylint: disable=cyclic-import
from PyUBCG.abc import AbstractHmmsearch
#pylint: enable=cyclic-import

LOGGER = logging.getLogger('PyUBCG.hmm_wrapper')

class Hmmsearch(AbstractHmmsearch):
    """
    Wrapper to hmmsearch
    """
    def __init__(self, config):
        self.config = config
        self._dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._output_folder = os.path.join(self._dirpath,
                                           config['paths']['hmmsearch_output'])
        self._input_path = os.path.join(*(self._dirpath,
                                          config['paths']['prodigal_output'],
                                          config['prefixes']['pro_prefix']))
        self._hmm_base = config['biological']['hmm_base']


    def run(self, file_path: str, **kwargs) -> None:
        """
        Method to execute hmmsearch
        :param path: some file here
        :kwargs: args to run program with
        :return:
        """
        LOGGER.info('Process %s file with hmmsearch.', file_path)
        process = subprocess.Popen(
            ['hmmsearch', '--noali', '--cut_tc', '-o',
             os.path.join(self._output_folder, file_path+'.out'), self._hmm_base,
             os.path.join(self._input_path, file_path)])
        process.wait()
