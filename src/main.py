# -*- coding: utf-8 -*-
"""
    This module implement main object to perform extract step of UBCG

"""

import argparse
# import logging
import logging.config

from src.abc_prodigal import ProdigalABC
from src.abc_hmmsearch import HmmsearchABC
from src.abc_config_loader import ConfigLoaderABC

logging.config.fileConfig('config/logging.conf')
LOGGER = logging.getLogger('PyUBCG')


class Main:
    """
    Main class to process extraction step. Equal to UBCG extract
    """

    def __init__(self):
        # pylint: disable=E0110
        LOGGER.info('Initialize Main object')
        LOGGER.info('Load config')
        self._load_args()
        self._config = ConfigLoaderABC(self._args)
        LOGGER.info('Initialize Program wrappers')
        self._prodigal = ProdigalABC(self._config)
        self._hmmsearch = HmmsearchABC(self._config)

    def _load_args(self):
        """
        Load arguments from command line, overwrite params in config
        :return:
        """
        parser = argparse.ArgumentParser(description='app')
        parser.add_argument('-c', '--config', default='config/config.yaml')
        parser.add_argument('-i', '--input_folder', default='fasta_input/')
        self._args = parser.parse_args()

    def _process_hmm_output_to_json(self):
        """
        Load hhmsearch output to jsons
        :return:
        """

    def _process_prodigal_output(self):
        """
        Prepare nuc and pro .fasta files before hmmsearch
        :return:
        """

    def bulk_run(self):
        """
        method to process extract step on every files in input folder
        :return:
        """

    def run(self, some_file):
        """
        Main method to perform all work
        :return:
        """
        self._prodigal.run(some_file)
        self._process_prodigal_output()
        self._hmmsearch.run(some_file)
        self._process_hmm_output_to_json()


if __name__ == '__main__':
    APP = Main()
    # app.run()
