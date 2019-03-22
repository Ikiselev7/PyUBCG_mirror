# -*- coding: utf-8 -*-
"""
    This module hold object to process build tree step pipeline

"""

import logging
import os

from Bio import Phylo
from Bio.Phylo import Consensus

from PyUBCG.fasta_seq_list import FastaSeqList
from PyUBCG.fasttree_wrapper import FastTree

LOGGER = logging.getLogger('PyUBCG.tree_builder')


class TreeBuilder:
    """
        Class to process build gene trees with FastTree
    """

    def __init__(self, config, replace_map):
        self._bcg_num = 0
        self.config = config
        self.replace_map = replace_map
        self._args_tree = self._get_tree_arguments()

        self._dirpath = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        self._target_gene_list = []

        self._tree_input_dir = os.path.join(
            self._dirpath, self.config.paths.align_concatenating_output,
            self.config.align_prefix)
        self._all_trees_input_dir = os.path.join(
            self._dirpath, self.config.paths.align_filtering_output,
            self.config.align_prefix)
        self._align_output_dir = os.path.join(
            self._dirpath, self.config.paths.align_output,
            self.config.align_prefix)
        self._tree_output_dir = os.path.join(
            self._dirpath, self.config.paths.align_trees_output,
            self.config.align_prefix)
        self._tree_input_file = os.path.join(self._tree_input_dir,
                                             'UBCG' +
                                             self.config.postfixes
                                             .align_align_const)

    def run(self):
        """Main method to process build tree step"""
        LOGGER.info("Reconstructing the final tree..")
        if os.path.isfile(self._tree_input_file) is False:
            LOGGER.error("The input file (concatenated sequence) "
                         "for running FastTree doesn't exist!")
            raise FileExistsError(f"The input file {self._tree_input_file} "
                                  f"for FastTree doesn't exist")
        fsl = FastaSeqList(self._tree_input_file)
        if fsl.get_seq_list_len() < 4:
            LOGGER.error('Too few species for building tree')
            raise ValueError('Too few species for FastTree')

        ft = FastTree(self.config)
        ft.run(self._tree_input_file, tree_args=self._args_tree,
               output_file=os.path.join(self._align_output_dir, 'PyUBCG' +
                                        self.config.postfixes.align_tree_const))

        self._reconstruct_gene_trees()
        self._make_all_gene_trees()
        if self.config.draw:
            tree = Phylo.read(os.path.join(self._align_output_dir, 'PyUBCG' +
                                           self.config.postfixes.align_tree_const), 'newick')
            Phylo.draw(tree,
                       savefig={'fname': os.path.join(self._align_output_dir,
                                                      self.config.align_prefix+'.png'),
                                'dpi': 300, 'bbox_inches': 'tight'})

        # FIXME
        # self._calculate_gsi()

    def _build_multiple_tree(self):
        """
        Method for multiple running FastTree
        :return:
        """
        for bcg in self._target_gene_list:
            tree_input_file = os.path.join(self._all_trees_input_dir,
                                           bcg+self.config.postfixes.
                                           align_align_const)
            tree_output_file = os.path.join(self._tree_output_dir, bcg +
                                            self.config.postfixes.
                                            align_tree_const)
            ft = FastTree(self.config)
            ft.run(tree_input_file, tree_args=self._args_tree,
                   output_file=tree_output_file)

    # pylint: disable=unnecessary-lambda
    def _get_tree_arguments(self):
        """
        Method for generating arguments for FastTree
        depend on model and align_mode
        :return: list of args
        """
        get_args = {
            'get_args': lambda model, mode:
                        [get_args['have_model'], get_args['no_model']][model is None]
                        (model, mode),
            'have_model': lambda x, y: get_args[x.lower()],
            'no_model': lambda x, y: [] if y == 'aa' else get_args['gtrcat'],
            'jttcat': [],
            'lgcat': ['-lg'],
            'wagcat': ['-wag'],
            'jttgamma': ['-gamma'],
            'lggamma': ['-lg', '-gamma'],
            'waggamma': ['-wag', '-gamma'],
            'jccat': ['-nt'],
            'gtrcat': ['-nt', '-gtr'],
            'jcgamma': ['-nt', '-gamma'],
            'gtrgamma': ['-nt', '-gtr', '-gamma'],
        }
        args = get_args['get_args'](self.config.model,
                                    self.config.align_mode)
        return args
    # pylint: enable=unnecessary-lambda

    def _reconstruct_gene_trees(self):
        """
        Method to build gene trees for each bcg
        :return:
        """
        LOGGER.info("Reconstructing gene trees..")
        fsl = FastaSeqList(self._tree_input_file)
        LOGGER.info('The length of concatenated '
                    'alignment: %s', fsl.get_seq_len())

        ubcg_gene = self.config.biological.ubcg_gene
        for bcg in ubcg_gene:
            gene_tree_file = os.path.join(self._all_trees_input_dir,
                                          bcg+self.config.postfixes.
                                          align_align_const)
            if os.path.isfile(gene_tree_file) is True:
                fsl = FastaSeqList(gene_tree_file)
                if fsl.get_seq_list_len() >= 4:
                    self._bcg_num += 1
                    self._target_gene_list.append(bcg)
                    LOGGER.info('%s: %s', bcg, fsl.get_seq_len())

        LOGGER.info('The total number of gene'
                    'trees to be reconstructed: %s', self._bcg_num)
        self._build_multiple_tree()
        LOGGER.info('All of the gene trees were reconstructed.')

    def _make_all_gene_trees(self):
        """
        Method to build one tree for all genes
        :return:
        """
        merged_trees = []
        for bcg in self._target_gene_list:
            gene_tree_file = os.path.join(self._tree_output_dir,
                                          bcg+self.config.postfixes.
                                          align_tree_const)
            try:
                with open(gene_tree_file) as f:
                    merged_trees.append(f.readline()+'\n')
            except FileExistsError as ex:
                LOGGER.error('Cannot read a gene tree %s', gene_tree_file)
                raise ex

        all_gene_trees_file = os.path.join(self._align_output_dir,
                                           "all_gene.trees")

        with open(all_gene_trees_file, 'w') as f:
            f.write('.'.join(merged_trees))

    def _calculate_gsi(self):
        """
        Method for calculating Gene Support Indices
        :return:
        """
        LOGGER.info("Calculating Gene Support Indices (GSIs)"
                    " from the gene trees..")
        genome_num = 0
        bcg_dir = os.path.join(self._dirpath, self.config.bcg_dir)
        for file in os.listdir(bcg_dir):
            if file.endswith('.bcg'):
                genome_num += 1

        nwk_file = os.path.join(self._align_output_dir, "all_gene.trees")
        trees = Phylo.parse(nwk_file, 'newick')
        tree = Consensus.majority_consensus(trees,
                                            cutoff=(100-self.config.gsi_threshold) * genome_num/100)
        Phylo.draw_ascii(tree)
        ubcg_gsi_file = os.path.join(self._align_output_dir,
                                     f'UBCG_gsi({self._bcg_num}'
                                     f'){self.config.postfixes.align_tree_const}')
        with open(ubcg_gsi_file, 'w') as f:
            Phylo.write(tree, f, 'newick')

        LOGGER.info("The final tree marked with GSI was written"
                    " to %s", ubcg_gsi_file)
