# -*- coding: utf-8 -*-
"""
    This module implement main object to perform extract step of UBCG

"""

import json
import time
import os
# import logging
import logging.config
import click

from PyUBCG.abc import AbstractProdigal, AbstractHmmsearch, AbstractConfigLoader

logging.config.fileConfig('config/logging.conf')
LOGGER = logging.getLogger('PyUBCG')


class Main:
    """
    Main class to process extraction step. Equal to UBCG extract
    """
    def __init__(self, **kwargs):
        # pylint: disable=E0110
        LOGGER.info('Initialize Main object')
        LOGGER.info('Load config')
        self._dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._args = kwargs
        self._config = AbstractConfigLoader(self._args).get_config()
        LOGGER.info('Create program structure')
        self._init_program_structure()
        LOGGER.info('Initialize Program wrappers')
        self._prodigal = AbstractProdigal(self._config)
        self._hmmsearch = AbstractHmmsearch(self._config)


    def _init_program_structure(self):
        prodigal_folder = os.path.join(self._dirpath,
                                       self._config['paths']['prodigal_output'])
        if not os.path.exists(prodigal_folder):
            os.makedirs(prodigal_folder)
        prodigal_pro = os.path.join(prodigal_folder,
                                    self._config['prefixes']['pro_prefix'])
        prodigal_nuc = os.path.join(prodigal_folder,
                                    self._config['prefixes']['nuc_prefix'])
        if not os.path.exists(prodigal_pro):
            os.makedirs(prodigal_pro)
        if not os.path.exists(prodigal_nuc):
            os.makedirs(prodigal_nuc)
        hmm_output = os.path.join(self._dirpath,
                                  self._config['paths']['hmmsearch_output'])
        if not os.path.exists(hmm_output):
            os.makedirs(hmm_output)
        extract_output = os.path.join(self._dirpath,
                                      self._config['paths']['extract_output'])
        if not os.path.exists(extract_output):
            os.makedirs(extract_output)
        align_output = os.path.join(self._dirpath,
                                    self._config['paths']['extract_output'])
        if not os.path.exists(align_output):
            os.makedirs(align_output)


    def _process_hmm_output_to_json(self, file_path):
        """
        Load hhmsearch output to jsons
        currently this method copy UBCG processing of hmmsearch output
        :return:
        """
        data = {}
        features = self._load_features(file_path)
        with open(os.path.join(*(self._dirpath, self._config['paths']['hmmsearch_output'],
                                 file_path+'.out'))) as hmm_output:
            while True:
                line = hmm_output.readline()
                if not line:
                    break
                if line.strip().startswith('Query:'):
                    query = line.split()[1]
                if all(i in line.split() for i in ['E-value', 'score', 'bias', 'E-value', 'score']):
                    hmm_output.readline()

                    line = hmm_output.readline().split()
                    if not line:
                        continue
                    if 'E' in line[0]:
                        e_value = line[0].replace('E', 'e')
                    else:
                        e_value = line[0]
                    index = int(line[8].split('_')[-1])
                    full_name = line[8]
                    feature_pro = features[full_name][self._config['prefixes']['pro_prefix']]
                    feature_nuc = features[full_name][self._config['prefixes']['nuc_prefix']]
                    # from UBCG code is not clear what for stand here 1
                    if query in self._config['biological']['ubcg_gene']:
                        data[query] = [1, [
                            index, feature_pro, feature_nuc, e_value
                        ]]

        bcg = [
            {'uid': str(time.time())},  # in UBCG could be specified as arg
            {'label': self._config['label']},
            {'accession': self._config['accession']},
            {'taxon_name': self._config['taxon']},
            {'ncbi_name': None},  # is hardcode in UBCG
            {'strain_name': self._config['strain']},
            {'strain_type': self._config['type']},
            {'strain_property': None},  # is hardcode in UBCG
            {'taxonomy': self._config['taxonomy']},
            {'UBCG_target_gene_number|version': '92|v3.0'},  # is hardcode in UBCG
            {'n_ubcg': len(set(self._config['biological']['ubcg_gene']))},
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

        with open(os.path.join(*(self._dirpath,
                                 self._config['paths']['extract_output'],
                                 file_path.rsplit()[0]+'.bcg')), 'w') as bcg_file:
            json.dump(bcg, bcg_file)

    def _load_features(self, file_path):
        features_folders = (self._config['prefixes']['nuc_prefix'],
                            self._config['prefixes']['pro_prefix'])
        genes = {}
        for feature in features_folders:
            with open(os.path.join(*(self._dirpath,
                                     self._config['paths']['prodigal_output'],
                                     feature, file_path))) as feature_file:
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

    def multiple_extract(self):
        """
        method to process extract step on every files in input folder
        :return:
        """

    def extract(self):
        """
        Main method to perform all work
        :return:
        """
        file_path = self._config['input_file']
        self._prodigal.run(file_path)
        self._hmmsearch.run(file_path)
        self._process_hmm_output_to_json(file_path)


#pylint disable: line-too-long
@click.group(help='PyUBCG - python implementation of UBCG pipeline https://www.ezbiocloud.net/tools/ubcg')
def cli():
    """entry point"""

@cli.command()
@click.option('-i', '--input_file', required=True, help='Path to fasta file to be extracted')
@click.option('-c', '--config', required=False, default='config/config.yaml',
              help='Specify path to your config if it is not default ')
@click.option('-l', '--label', default=None,
              help='full label of the strain/genome. '
                   'It should be encompassed by single quotes (e.g. --label “Escherichia coli O157 876”).')
@click.option('-a', '--accession', default=None, help='accession of a genome sequence. '
                                                      'Usually, NCBI’s assembly accession is used for public domain data.')
@click.option('-t', '--taxon', default=None, help='name of species (e.g. --taxon “Escherichia coli”)')
@click.option('-tax', '--taxonomy', default=None, help='Taxonomy')
@click.option('-s', '--strain', default=None, help='name of the strain (e.g. --strain “JC 126”)')
@click.option('--type', default=False, is_flag=True,
              help='add this flag if a strain is the type strain of species or subspecies (e.g. --type)')
def extract(**kwargs):
    """
    Converting genome assemblies or contigs (fasta) to bcg files
    """
    app = Main(**kwargs)
    app.extract()

@cli.command()
@click.option('-bcg_dir', required=True, help="directory for bcg files that you want to include in the alignment.")
@click.option('-out_dir', help='directory where all output files will be')
@click.option('-a', type=click.Choice(['nt', 'aa', 'codon', 'codon12']), help='''nt: nucleotide sequence alignment
aa: amino acid sequence alignment
codon: codon-based alignment (output is nucleotide sequences, but alignment is carried out using amino acid sequences) DEFAULT.
codon12: same as “codon” option but only 1st and 2nd nucleotides of a codon are selected. The 3rd position is usually of high variability.
''')
@click.option('-t', type=int, help="number of process to be used (default=1)")
@click.option('-t', type=int, help="""set a filtering cutoff for gap-containing positions from 0 to 100 (default: 50)
-- 0 to select all alignment positions
-- 100 to select positions that are present in all genomes
-- 50 to select positions that are present in a half of genomes
""")
@click.option('--prefix', help="a prefix is to appended to all output files to recognize each different run. If you don’t designate, one will be generated automatically.")
@click.option('--gsi_threshold', type=int, help='Threshold for Gene Support Index (GSI). 95 means 95%. (default = 95)')
#@click.option('--raxml', help='Use RAxML for phylogeny reconstruction (Default: FastTree). Be aware that RAxML is much slower than FastTree.')
#@click.option('--zZ', help='Make zZ-formatted files. This additionally creates fasta/nwk files with zZ+uid+zZ format for the names of each genome')
def align(**kwargs):
    """
    Generating multiple alignments from bcg files
    """
    app = Main(**kwargs)
    app.align()
#pylint enable: line-too-long


if __name__ == '__main__':
    cli()

    # APP._process_hmm_output_to_json('CP012646_s_GCA_001281025.1_KCOM_1350.fasta')
    # app.run()
