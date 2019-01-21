# -*- coding: utf-8 -*-
"""
    This module implement main object to perform extract step of UBCG

"""

import argparse
import json
import time
# import logging
import logging.config

from PyUBCG.abc_prodigal import ProdigalABC
from PyUBCG.abc_hmmsearch import HmmsearchABC
from PyUBCG.abc_config_loader import ConfigLoaderABC

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
        parser = argparse.ArgumentParser(
            description='PyUBCG is python implementation of UBCG pipeline https://www.ezbiocloud.net/tools/ubcg',
            prog='pyubcg'
        )
        subparsers = parser.add_subparsers(
            help='choose one of this command',
            dest='command'
        )

        parser_extract = subparsers.add_parser(
            'extract',
            description='Converting genome assemblies or contigs (fasta) to bcg files',
            help='converts a fasta file to bcg file using prodigal and hmmsearch')
        parser_extract.add_argument(
            '-i', '--input_file',
            required=True,
            help='Path to fasta file to be extracted'
        )
        parser_extract.add_argument(
            '-c', '--config',
            default='config/config.yaml',
            help='Specify path to your config if it is not default '
        )
        parser_extract.add_argument(
            '-l', '--label',
            default=None,
            help='full label of the strain/genome. It should be encompassed by single quotes (e.g. --label “Escherichia coli O157 876”).'
        )
        parser_extract.add_argument(
            '-a', '--acc',
            default=None,
            help='accession of a genome sequence. Usually, NCBI’s assembly accession is used for public domain data.'
        )
        parser_extract.add_argument(
            '-t', '--taxon',
            default=None,
            help='name of species (e.g. --taxon “Escherichia coli”)'
        )
        parser_extract.add_argument(
            '-s', '--strain',
            default=None,
            help='name of the strain (e.g. --strain “JC 126”)'
        )
        parser_extract.add_argument(
            '--type',
            default=False,
            action='store_true',
            help='add this flag if a strain is the type strain of species or subspecies (e.g. --type)'
        )

        parser_align = subparsers.add_parser(
            'align',
            description='Generating multiple alignments from bcg files',
            help='align help'
        )


        self._args = parser.parse_args()

    def _process_hmm_output_to_json(self, file_path):
        """
        Load hhmsearch output to jsons
        currently this method copy UBCG processing of hmmsearch output
        :return:
        """
        data = {}
        features = self._load_features(file_path)
        with open(f'{self._config.hmmsearch_output}/{file_path}.out') as hmm_output:
            while True:
                line = hmm_output.readline()
                if not line:
                    break
                if line.strip().startswith('Query:'):
                    query = line.split()[1]
                if all(i in line.split() for i in ['E-value', 'score', 'bias', 'E-value', 'score']):
                    hmm_output.readline()
                    line = hmm_output.readline().split()
                    e_value = line[0].replace('E', 'e')  # lowercase e is in original ubcg
                    index = int(line[8].split('_')[-1])
                    full_name = line[8]
                    feature_pro = features[full_name][self._config.pro_prefix]
                    feature_nuc = features[full_name][self._config.nuc_prefix]
                    # from UBCG code is not clear what for stand here 1
                    if query in self._config.ubcg_gene:
                        data[query] = [1, [
                            index, feature_pro, feature_nuc, e_value
                        ]]

        bcg = [
            {'uid': str(time.time())},  # in UBCG could be specified as arg
            {'label': self._config.label},
            {'accession': self._config.acc},
            {'taxon_name': self._config.taxon},
            {'ncbi_name': None},  # is hardcode in UBCG
            {'strain_name': self._config.strain},
            {'strain_type': self._config.type},
            {'strain_property': None},  # is hardcode in UBCG
            {'taxonomy': self._config.taxonomy},
            {'UBCG_target_gene_number|version': '92|v3.0'},  # is hardcode in UBCG
            {'n_ubcg': len(set(self._config.ubcg_gene))},
            {'n_genes': len(data)},  # len of hmm result
            {'n_paralog_ubcg': None},  # UbcgDomain Integer getN_paralog_ubcg()
            {'data_structure': {
                'gene_name': [
                    'n_genes', [
                        'feature_index',
                        'dna',
                        'protein',
                        'evalue'
                    ]
                ]}
            },
            {'data': data},
        ]

        with open(f'extract_to_json/{file_path}', 'w') as bcg_file:
            json.dump(bcg, bcg_file)


    def _load_features(self, file_path):
        features_folders = self._config.nuc_prefix, self._config.pro_prefix
        genes = {}
        for feature in features_folders:
            with open(f'{self._config.prodigal_output}/{feature}/{file_path}') as feature_file:
                data = feature_file.readlines()
                for line in data:
                    if line.startswith('>'):
                        chunk = line.split()[0][1:]
                        if chunk not in genes:
                            genes[chunk] = {features_folders[0]: '', features_folders[1]: ''}
                    else:
                        if '*' in line:
                            line = line.replace('*', '')
                        genes[chunk][feature] = genes[chunk].get(feature, '') + line.strip()
        return genes

    def align(self):
        """
        Align step
        :return:
        """

    def bulk_run(self):
        """
        method to process extract step on every files in input folder
        :return:
        """

    def run(self):
        if self._config.command == 'extract':
            self.extract()
        if self._config.command == 'align':
            self.align()


    def extract(self):
        """
        Main method to perform all work
        :return:
        """
        file_path = self._config.input_file.split('/')[-1]
        self._prodigal.run(file_path)
        self._hmmsearch.run(file_path)
        self._process_hmm_output_to_json(file_path)

if __name__ == '__main__':
    APP = Main()

    # APP._process_hmm_output_to_json('CP012646_s_GCA_001281025.1_KCOM_1350.fasta')
    # app.run()
