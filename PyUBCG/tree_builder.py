import logging
import os

from PyUBCG.fasta_seq_list import FastaSeqList
from PyUBCG.fasttree_wrapper import FastTree
from PyUBCG.label_replacer import LabelReplacer
LOGGER = logging.getLogger('PyUBCG.tree_builder')


class TreeBuilder:

    def __init__(self, config, replace_map):
        self._bcg_num = 0
        self.config = config
        self.replace_map = replace_map

        self._dirpath = os.path.dirname(
            os.path.dirname(os.path.abspath(__file__)))
        if self.config.prefix is None:
            self._run_id = self.config.run_id
        else:
            self._run_id = self.config.prefix
        self._target_gene_list = []

        self._tree_input_dir = os.path.join(
            self._dirpath, self.config.paths.align_align_output)
        self._tree_output_dir = os.path.join(
            self._dirpath, self.config.paths.align_output)
        self._tree_input_file = os.path.join(self._tree_input_dir,
                                             f'{self._run_id}.UBCG'
                                             f'.{self.config.align_mode}'
                                             f'.{self.config.filter}.zZ.fasta')

    def run(self):
        LOGGER.info("Reconstructing the final tree..")
        if os.path.isfile(self._tree_input_file) is False:
            LOGGER.error("The input file (concatenated sequence) "
                         "for running FastTree doesn't exist!")
            raise FileExistsError(f"The input file {self._tree_input_file} "
                                  f"for FastTree doesn't exist")

        fsl = FastaSeqList(self._tree_input_file)
        fsl.parse_file()
        if fsl.get_seq_list_len() < 4:
            LOGGER.error('Too few species for building tree')
            raise ValueError('Too few species for FastTree')

        args_tree = self._get_tree_arguments(self._tree_input_file, 'UBCG')
        ft = FastTree(self.config)
        ft.run(self._tree_input_file, tree_args=args_tree)
        self._reconstruct_gene_trees()
        self._make_all_gene_trees()
        self._calculate_gsi()

    def _build_multiple_tree(self):
        for bcg in self._target_gene_list:
            tree_input_file = self._get_input_tree_file(bcg)
            args = self._get_tree_arguments(tree_input_file, bcg)
            ft = FastTree(self.config)
            ft.run(tree_input_file, tree_args=args)

    def _get_tree_arguments(self, tree_input_file, bcg):
        tree_output_file = os.path.join(self._tree_output_dir,
                                        f'{self._run_id}.{bcg}'
                                        f'.{self.config.align_mode}'
                                        f'.{self.config.filter}.zZ.nwk')
        args = []
        if self.config.model is None:
            if self.config.align_mode == 'aa':
                args = []
            else:
                args = ['-nt', '-gtr']
        else:
            model = self.config.model.lower()
            if self.config.align_mode == 'aa':
                if model == 'jttcat':
                    args = []
                elif model == 'lgcat':
                    args = ['-lg']
                elif model == 'wagcat':
                    args = ['-wag']
                elif model == 'jttgamma':
                    args = ['-gamma']
                elif model == 'lggamma':
                    args = ['-lg', '-gamma']
                elif model == 'waggamma':
                    args = ['-wag', '-gamma']
            if model == 'jccat':
                args = ['-nt']
            if model == 'gtrcat':
                args = ['-nt', '-gtr']
            if model == 'jcgamma':
                args = ['-nt', '-gamma']
            if model == 'gtrgamma':
                args = ['-nt', '-gtr']
        tree_args = ['FastTree'] + args + [tree_input_file,
                                           '>', tree_output_file]
        return tree_args

    def _get_input_tree_file(self, bcg):
        if self.config.align_mode == 'aa':
            gene_tree_file = self._run_id + ".align." + bcg + \
                             ".protein." + self.config.filter + ".zZ.fasta"
        elif self.config.align_mode == 'nt':
            gene_tree_file = self._run_id + ".align." + bcg + \
                             ".dna." + self.config.filter + ".zZ.fasta"
        elif self.config.align_mode == 'codon':
            gene_tree_file = self._run_id + ".align." + bcg + \
                             ".codon." + self.config.filter + ".zZ.fasta"
        elif self.config.align_mode == 'codon12':
            gene_tree_file = self._run_id + ".align." + bcg + \
                             ".codon12." + self.config.filter + ".zZ.fasta"
        else:
            LOGGER.error('Unknown align mode is selected')
            raise ValueError('Unknown align mode is selected')
        return os.path.join(self._tree_input_dir, gene_tree_file)

    def _reconstruct_gene_trees(self):
        LOGGER.info("Reconstructing gene trees..")
        con_fsl = FastaSeqList(self._tree_input_file)
        con_fsl.parse_file()
        LOGGER.info(f'The length of concatenated '
                    f'alignment: {con_fsl.get_seq_len()}')

        ubcg_gene = self.config.biological.ubcg_gene
        n = 0
        while n < len(ubcg_gene):
            bcg = ubcg_gene[n]
            gene_tree_file = self._get_input_tree_file(bcg)
            json_file = self._tree_output_dir+gene_tree_file
            if os.path.isfile(json_file):
                fsl = FastaSeqList(json_file)
                fsl.parse_file()
                if fsl.get_seq_list_len() >= 4:
                    self._bcg_num += 1
                    self._target_gene_list.append(bcg)
                    LOGGER.info(bcg + ": " + fsl.get_seq_len())

        LOGGER.info(f"The total number of gene "
                    f"trees to be reconstructed: {self._bcg_num}")
        self._build_multiple_tree()
        LOGGER.info('All of the gene trees were reconstructed.')

    def _make_all_gene_trees(self):
        merged_trees = []
        for bcg in self._target_gene_list:
            gene_tree_file = os.path.join(self._tree_output_dir,
                                          f'{self._run_id}.{bcg}'
                                          f'.{self.config.align_mode}'
                                          f'.{self.config.filter}.zZ.nwk')

            try:
                with open(gene_tree_file) as f:
                    merged_trees.append(f.readline()+'\n')
            except FileExistsError as ex:
                LOGGER.error(f'Cannot read a gene tree{gene_tree_file}')
                raise ex

        all_gene_trees_file = os.path.join(self._tree_output_dir, self._run_id,
                                           ".all_gene.trees")

        with open(all_gene_trees_file, 'w') as f:
            f.write('.'.join(merged_trees))

    def _calculate_gsi(self):
        LOGGER.info("Calculating Gene Support Indices (GSIs)"
                    " from the gene trees..")
        genome_num = 0
        bcg_dir = os.path.join(self._dirpath, self.config.bcg_dir)
        for file in os.listdir(bcg_dir):
            if file.endswith('.bcg'):
                genome_num += 1

        # TODO call lumberjack
        tmp = ''

        ubcg_gsi_file = os.path.join(self._tree_output_dir, f'{self._run_id}.'
                                     f'UBCG_gsi({self._bcg_num})'
                                     f'.{self.config.align_mode}'
                                     f'.{self.config.filter}.zZ.nwk', )
        with open(ubcg_gsi_file, 'w') as f:
            f.write(tmp)

        bcg_file = os.path.join(self._tree_output_dir, self._run_id)
        temp_json = {}
        with open(bcg_file) as f:
            temp_json['UBCG'] = f.readline()

            for bcg in self._target_gene_list:
                gene_tree_file = os.path.join(self._tree_output_dir,
                                              f'{self._run_id}.{bcg}'
                                              f'.{self.config.align_mode}'
                                              f'.{self.config.filter}.zZ.nwk')
                with open(gene_tree_file) as tree_file:
                    tree = tree_file.readline()
                    temp_json[bcg] = tree
        self._change_labels()
        LOGGER.info(f"The final tree marked with GSI was written"
                    f" to {ubcg_gsi_file.replace('.zZ.', '.label.')}")

    def _change_labels(self):
        label_replacer = LabelReplacer(self.config, self.replace_map)
        align_mode = self.config.align_mode
        input_files = list()
        input_files.append(os.path.join(self._tree_output_dir,
                                        f'{self._run_id}.UBCG.{align_mode}'
                                        f'.{self.config.filter}.'
                                        f'zZ.fasta'))

        input_files.append(os.path.join(self._tree_output_dir,
                                        f'{self._run_id}.UBCG.{align_mode}'
                                        f'.{self.config.filter}.zZ.nwk'))

        input_files.append(os.path.join(self._tree_output_dir,
                                        f'{self._run_id}.UBCG_gsi'
                                        f'({self._bcg_num}).{align_mode}'
                                        f'.{self.config.filter}.zZ.nwk'))

        for bcg in self.config.biological.ubcg_gene:
            aligned_gene_file = os.path.join(self._tree_output_dir,
                                             f'{self._run_id}.align'
                                             f'.{bcg}.{align_mode}'
                                             f'.{self.config.filter}'
                                             f'.zZ.fasta')
            tree_file = os.path.join(self._tree_output_dir,
                                     f'{self._run_id}.{bcg}.'
                                     f'{align_mode}.{self.config.filter}'
                                     f'.zZ.nwk')
            if align_mode == 'nt':
                aligned_gene_file = os.path.join(self._tree_output_dir,
                                                 f'{self._run_id}.align'
                                                 f'.{bcg}.dna'
                                                 f'.{self.config.filter}'
                                                 f'.zZ.fasta')
            if align_mode == 'aa':
                aligned_gene_file = os.path.join(self._tree_output_dir,
                                                 f'{self._run_id}.align'
                                                 f'.{bcg}.protein'
                                                 f'.{self.config.filter}'
                                                 f'.zZ.fasta')

            if os.path.isfile(aligned_gene_file) is True:
                input_files.append(aligned_gene_file)
            if os.path.isfile(tree_file) is True:
                input_files.append(tree_file)

        for input_file in input_files:
            label_replacer.replace_name(input_file,
                                        input_file.replace('.zZ.', '.label.'),
                                        self.config.zZ)
