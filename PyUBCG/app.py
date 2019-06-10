# -*- coding: utf-8 -*-
"""
    This module implement main object to perform extract step of UBCG

"""

import json
import time
import os
import sys
import shutil
# import logging
import logging.config
import click

from PyUBCG.abc import AbstractProdigal, AbstractHmmsearch, \
    AbstractConfigLoader, AbstractMafft
from PyUBCG.aligner import Aligner
from PyUBCG.bcg_dto import BcgDto, BcgGenData, BcgDtoEncoder
from PyUBCG.tree_builder import TreeBuilder

logging.config.fileConfig('config/logging.conf')
LOGGER = logging.getLogger('PyUBCG')


class Main:
    """
    Main class to process extraction step. Equal to UBCG extract
    """
    def __init__(self, command, **kwargs):
        # pylint: disable=E0110
        LOGGER.info('Initialize Main object')
        LOGGER.info('Load config')
        self._dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._args = kwargs
        self._config = AbstractConfigLoader(self._args).get_config()
        self._config['command'] = command
        LOGGER.info('Create program structure')
        if command == 'align':
            if os.path.exists(os.path.join(self._dirpath,
                                           self._config.paths.align_output,
                                           self._config.align_prefix)) and not self._config.rewrite:
                sys.stderr.write(
                    f'Given prefix {self._config.align_prefix} alredy exist. '
                    'Use another one or add -R flag to rewrite existing files.\n\t'
                    'WARNING! All existing files will be deleted.\n')
                sys.exit(1)
            self._flush_prefix_folders()
        self._init_program_structure()
        LOGGER.info('Initialize Program wrappers')
        self._prodigal = AbstractProdigal(self._config)
        self._hmmsearch = AbstractHmmsearch(self._config)
        if command == 'align':
            self._mafft = AbstractMafft(self._config)
            self._aligner = Aligner(self._config)
            self._replace_map = {}
            self._tree_builder = TreeBuilder(self._config, self._replace_map)


    def _flush_prefix_folders(self):
        if self._config.rewrite:
            for folder in self._config['paths']:
                prefix_folder = os.path.join(self._dirpath,
                                             folder,
                                             self._config.align_prefix)
                if os.path.exists(prefix_folder):
                    shutil.rmtree(prefix_folder)


    def _init_program_structure(self):
        for folder in self._config['paths']:
            if self._config.command == 'extract' and folder.startswith('align'):
                continue
            path = os.path.join(self._dirpath,
                                self._config['paths'][folder])
            if folder.startswith('align'):
                path = os.path.join(self._dirpath, self._config['paths'][folder], self._config.prefixes.align_prefix)
            if not os.path.exists(path):
                os.makedirs(path)


    def _process_hmm_output_to_json(self, file_path):
        """
        Load hhmsearch output to jsons
        currently this method copy UBCG processing of hmmsearch output
        :return:
        """
        data = []
        features = self._load_features(file_path)
        with open(os.path.join(self._dirpath, self._config['paths']['hmmsearch_output'],
                               file_path+'.out')) as hmm_output:
            while True:
                line = hmm_output.readline()
                if not line:
                    break
                if line.strip().startswith('Query:'):
                    gene = line.split()[1]
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
                    # 1 here in origin to determine later if gene contains
                    # in genome
                    if gene in self._config['biological']['ubcg_gene']:
                        data.append(BcgGenData(
                            name=gene,
                            n_genes=1,
                            index=index,
                            dna=feature_nuc,
                            protein=feature_pro,
                            evalue=e_value,
                        ))

        bcg_dto = BcgDto(
            uid=str(time.time()),
            label=self._config['label'],
            accession=self._config['accession'],
            taxon_name=self._config['taxon'],
            ncbi_name=None, #  is hardcode in origin
            strain_name=self._config['strain'],
            strain_type=self._config['type'],
            strain_property=None, #  is hardcode in origin
            taxonomy=self._config['taxonomy'],
            n_ubcg=len(set(self._config['biological']['ubcg_gene'])),
            n_genes=len(data),
            n_paralog_ubcg=None, #  UbcgDomain Integer getN_paralog_ubcg()
            UBCG_target_gene_number=92,
            version=1.0,
            data=data,
        )

        with open(os.path.join(*(self._dirpath,
                                 self._config['paths']['extract_output'],
                                 ''.join(file_path.rsplit('.')[:-1])+'.bcg')),
                  'w') as bcg_file:
            json.dump(bcg_dto, bcg_file,
                      cls=BcgDtoEncoder,
                      indent=4 if self._config.format else 0)


    def _load_features(self, file_path):
        features_folders = (self._config['prefixes']['pro_prefix'],
                            self._config['prefixes']['nuc_prefix'])
        genes = {}
        for feature in features_folders:
            with open(os.path.join(*(self._dirpath,
                                     self._config['paths']['prodigal_output'],
                                     feature, file_path))) as feature_file:
                data = feature_file.readlines()
                for line in data:
                    if line.startswith('>'):
                        gene = line.split()[0][1:]
                        if gene not in genes:
                            genes[gene] = {features_folders[0]: '', features_folders[1]: ''}
                    else:
                        if '*' in line:
                            line = line.replace('*', '')
                        genes[gene][feature] = genes[gene].get(feature, '') + line.strip()
        return genes

    def align(self):
        """
        Align step
        :return:
        """
        self._replace_map = self._aligner.run()
        self._tree_builder.replace_map = self._replace_map
        self._tree_builder.run()


    def multiple_extract(self):
        """
        method to process extract step on every files in input folder
        :return:
        """
        fastas = os.listdir(os.path.join(self._dirpath,
                                         self._config.paths.fasta_input_folder))
        self._config.accession = None
        self._config.taxon = None
        self._config.taxonomy = None
        self._config.strain = None
        self._config.format = None
        self._config.type = None
        for fasta in fastas:
            name = fasta.split('/')[-1].rsplit('.', 1)[0]
            self._config.label = name
            self.extract(fasta)


    def extract(self, file_path=None):
        """
        Main method to perform all work
        :return:
        """
        file_path = self._config['input_file'] if not file_path else file_path
        self._prodigal.run(file_path)
        self._hmmsearch.run(file_path)
        self._process_hmm_output_to_json(file_path)


#pylint disable: line-too-long
@click.group(help='PyUBCG - python implementation of UBCG pipeline https://www.ezbiocloud.net/tools/ubcg')
def cli():
    """entry point for pyubcg"""

@cli.command()
@click.option('-i', '--input_file', required=True, help='Path to fasta file to be extracted')
@click.option('-o', '--extract_output', default='extract_output', help="directory for created bcg files")
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
@click.option('--format', default=False, is_flag=True,
              help='add this flag if you want to add indent to produced bcg-jsons')
def extract(**kwargs):
    """
    Converting genome assemblies or contigs (fasta) to bcg files
    """
    app = Main(**kwargs, command='extract')
    app.extract()


@cli.command()
@click.option('-o', '--extract_output', default='extract_output', help="directory for created bcg files")
@click.option('-i', '--fasta_input_folder', required=True, help='Path to fastas files to be extracted.')
@click.option('-c', '--config', default='config/config.yaml',
              help='Specify path to your config if it is not default')
@click.option('--format', default=False, is_flag=True,
              help='add this flag if you want to add indent to produced bcg-jsons')
def multiple_extract(**kwargs):
    """
    Converting genomes assemblies or contigs (fasta) to bcg files in given folder.
    """
    app = Main(**kwargs, command='extract')
    app.multiple_extract()


@cli.command()
@click.option('--bcg_dir', default='extract_output', help="directory for bcg files that you want to include in the alignment.")
@click.option('-c', '--config', required=False, default='config/config.yaml',
              help='Specify path to your config if it is not default ')
@click.option('-o', '--out_dir', default='align_output', help='directory where all output files will be')
@click.option('-a', '--align_mode', type=click.Choice(['nt', 'aa', 'codon', 'codon12']), default='codon',
              help='''nt: nucleotide sequence alignment
aa: amino acid sequence alignment
codon: codon-based alignment (output is nucleotide sequences, but alignment is carried out using amino acid sequences) DEFAULT.
codon12: same as “codon” option but only 1st and 2nd nucleotides of a codon are selected. The 3rd position is usually of high variability.
''')
@click.option('-t', type=int, help="number of process to be used (default=1)")
@click.option('-f', '--filter', type=click.IntRange(min=0, max=100),
              default=50, help="""set a filtering cutoff for gap-containing positions from 0 to 100 (default: 50)
-- 0 to select all alignment positions
-- 100 to select positions that are present in all genomes
-- 50 to select positions that are present in a half of genomes
""")
@click.option('-m', '--model', default=None,
              help="""A model used to infer trees
              For FastTree - NUCLEOTIDE sequences 
                  JCcat, GTRcat, JCgamma, GTRgamma
              For FastTree - AMINO ACID sequences 
                  JTTcat, LGcat, WAGcat, JTTgamma, LGgamma, WAGgamma""")
@click.option('--align_prefix', help="a prefix is to appended to all output files to recognize each different run. If you don’t designate, one will be generated automatically.")
@click.option('--gsi_threshold', type=click.IntRange(min=0, max=100),
              default=95, help='Threshold for Gene Support Index (GSI). 95 means 95%. (default = 95)')
@click.option('-R', '--rewrite', default=False, is_flag=True,
              help='add this flag if you want to rewrite existing files after previous run.')
@click.option('-d', '--draw', default=False, is_flag=True,
              help='Add this flag if you want to see created tree on plot.')
#@click.option('--raxml', help='Use RAxML for phylogeny reconstruction (Default: FastTree). Be aware that RAxML is much slower than FastTree.')
#@click.option('--zZ', help='Make zZ-formatted files. This additionally creates fasta/nwk files with zZ+uid+zZ format for the names of each genome')
def align(**kwargs):
    """
        Generating multiple alignments from bcg files
    """

    app = Main(**kwargs, command='align')
    app.align()
#pylint enable: line-too-long


if __name__ == '__main__':
    cli()
    # APP._process_hmm_output_to_json('CP012646_s_GCA_001281025.1_KCOM_1350.fasta')
    # app.run()
