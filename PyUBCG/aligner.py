# -*- coding: utf-8 -*-
"""
    This module hold object to process align step pipeline

"""

import glob
import os
import json
import logging


from PyUBCG.fasta_seq_list import FastaSeqList
from PyUBCG.abc import AbstractMafft


LOGGER = logging.getLogger('PyUBCG.aligner')

class Aligner:
    """
        Class to process multiple gene alignment with filtering
    """

    def __init__(self, config):
        self._dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self.config = config
        self._bcg_list = []
        self._genome_name_pro = []
        self._genome_name = []
        self._bcg_filtered_in_align = []
        self._bcg_num = 0
        self._mafft = AbstractMafft(self.config)
        self._genes_processed_with_mafft = []
        self._extract_dir = ''
        self._align_inputmerge_with_prefix = ''
        self._align_inputparse_with_prefix = ''
        self._align_filtering_output_with_prefix = ''
        self._align_mafft_output_with_prefix = ''
        self._align_align_with_prefix = ''
        self._merged_input_nuc = ''
        self._merged_input_pro = ''
        self._align_alignment_output = ''


    def run(self):
        """main method to process align step"""
        self._extract_dir = os.path.join(self._dirpath,
                                         self.config.bcg_dir)
        if not os.path.exists(self._extract_dir):
            raise ValueError('Extract folder not exist')
        if len(os.listdir(self._extract_dir)) < 4:
            raise ValueError('To few bcg to align')
        self._align_inputmerge_with_prefix = self._create_folder_if_not_exist(
            self.config.paths.align_input_merge,
            self.config.prefixes.align_prefix
        )
        self._align_inputparse_with_prefix = self._create_folder_if_not_exist(
            self.config.paths.align_input_parse,
            self.config.prefixes.align_prefix
        )
        self._align_filtering_output_with_prefix = self._create_folder_if_not_exist(
            self.config.paths.align_filtering_output,
            self.config.prefixes.align_prefix
        )
        self._align_mafft_output_with_prefix = self._create_folder_if_not_exist(
            self.config.paths.align_mafft_output,
            self.config.prefixes.align_prefix
        )
        self._align_align_with_prefix = self._create_folder_if_not_exist(
            self.config.paths.align_align_output,
            self.config.prefixes.align_prefix
        )
        self._align_alignment_output = self._create_folder_if_not_exist(
            self.config.paths.align_alignment_output,
            self.config.prefixes.align_prefix
        )


        replace_map = self._input_merge()
        self._input_parsing()
        self._align()
        self._concatenating()
        return replace_map


    def _input_merge(self):
        """
        Method to reconstruct fasta file like after prodigal output but
        only with filtered genes.
        :return:
        """
        check_label = {}
        replace_map = {}

        for extracted_file in glob.glob(self._extract_dir+'/*'):
            with open(extracted_file) as bcg_file:
                bcg = json.load(bcg_file)
            target_value = 'data', 'uid', 'label'
            #  filter bcg to get only needed values
            # data = {key: value for item in bcg for key, value in item.items()
            #         if any(param in item for param in target_value)}
            data = {key: bcg[key] for key in target_value}
            #  like in original ubcg
            data['uid'] = 'zZ' + data['uid'] + 'zZ'
            # this is copypast fro, origin probably to check if we have duplicate labels
            check_label[data['uid']] = check_label.get(data['uid'], 0) + 1
            if check_label[data['uid']] != 1:
                data['label'] = data['label'] + '_' + check_label[data['uid']]
            replace_map[data['uid']] = data['label']
            self._merged_input_nuc = os.path.join(
                self._align_inputmerge_with_prefix,
                self.config.prefixes.nuc_input + self.config.postfixes.nuc_input_const)
            self._merged_input_pro = os.path.join(
                self._align_inputmerge_with_prefix,
                self.config.prefixes.pro_input + self.config.postfixes.pro_input_const)
            with open(self._merged_input_nuc, 'a+') as nuc_file, \
                    open(self._merged_input_pro, 'a+') as pro_file:
                nuc_file.write('#'+data['uid']+'\n')
                pro_file.write('#'+data['uid']+'\n')
                for gene in data['data']:
                    #  in origin they collect all UBCG in bcg, even if
                    #  genome does not have them, this check is to server original bcg
                    if data['data'][gene][0] != 0:
                        nuc_file.write('>'+gene+'\n')
                        pro_file.write('>'+gene+'\n')
                        nuc_file.write(data['data'][gene][1]['nuc_sequence']+'\n')
                        pro_file.write(data['data'][gene][1]['pro_sequence']+'\n')
            LOGGER.info('Wrote merged nucleotide file %s', self._merged_input_nuc)
            LOGGER.info('Wrote merged protein file %s', self._merged_input_pro)
        return replace_map


    def _input_parsing(self):
        """
        Method to create fasta-like files to each gene from genomes.
        :return:
        """

        def read_pro_file():
            """
            Method to create map with gene_name:sequence from file with
            nucleotide
            :return:
            """
            fasta_map_pro = {}
            genome_names_protein = []
            with open(self._merged_input_pro) as pro_file:
                for line in pro_file:
                    if line.startswith('#'):
                        genome_name = line[1:].strip()
                        genome_names_protein.append(genome_name)
                    elif line.startswith('>'):
                        gene = line[1:].strip()
                    else:
                        seq_pro = line.strip()
                        new_record = '>' + genome_name + '\n' + seq_pro + '\n'
                        fasta_map_pro[gene] = fasta_map_pro.get(gene, '') + new_record
            return fasta_map_pro, genome_names_protein


        def read_nuc_file():
            """
            Method to create map with gene_name:sequence from file with
            nucleotide
            :return:
            """
            fasta_map_nuc = {}
            genome_names = []
            with open(self._merged_input_nuc) as nuc_file:
                for line in nuc_file:
                    if line.startswith('#'):
                        genome_name = line[1:].strip()
                        genome_names.append(genome_name)
                    elif line.startswith('>'):
                        gene = line[1:].strip()
                    else:
                        seq = line.strip()
                        #  stop codon
                        if (not seq.endswith('TAA') or not seq.endswith('TAG')
                                or not seq.endswith('TGA')):
                            seq = seq + '---'
                        new_record = '>' + genome_name + '\n' + seq + '\n'
                        fasta_map_nuc[gene] = fasta_map_nuc.get(gene, '') + new_record
            return fasta_map_nuc, genome_names

        def write_file_from_map(map_data, postfix):
            """
            Write file for every core gene encountered in every genome
            :param map_data:
            :param postfix:
            :return:
            """
            bcg_list = []
            for gene in map_data:
                bcg_list.append(gene)
                file_path = os.path.join(self._align_inputparse_with_prefix, gene+postfix)
                with open(file_path, 'w') as gene_file:
                    gene_file.write(map_data[gene])

                LOGGER.info('Wrote fasta file with gene %s, path %s', gene, file_path)
            return bcg_list

        if self.config['align_mode'] == 'nt':
            LOGGER.info('prosess input parse, align mode %s', self.config.align_mode)
            fasta_map_nuc, self._genome_name = read_nuc_file()
            self._bcg_list = write_file_from_map(
                fasta_map_nuc, self.config.postfixes.input_parsing_dna_const)

        elif self.config['align_mode'] in ('codon', 'codon12', 'aa'):
            LOGGER.info('prosess input parse, align mode %s', self.config.align_mode)
            fasta_map_pro, self._genome_name_pro = read_pro_file()
            fasta_map_nuc, self._genome_name = read_nuc_file()
            # this check is copy-past from origin
            if len(fasta_map_nuc) != len(fasta_map_pro):
                #  probably do something with recently created files here
                raise ValueError('Error: The number of genomes for protein/nucleotide '
                                 'sequences are not identical.')
            if self.config.align_mode != 'aa':
                #  this step is specific to codon and codon12 mode
                write_file_from_map(fasta_map_nuc, self.config.postfixes.input_parsing_dna_const)
            self._bcg_list = write_file_from_map(
                fasta_map_pro, self.config.postfixes.input_parsing_pro_const)


    def _align(self):
        """
        Step to process multiple sequences alignment and run filter gap after it
        :return:
        """
        def filter_genomes_by_frequency(postfix):
            filtered_bcg = []
            bcg_num = 0
            for gene in self._bcg_list:
                bcg = os.path.join(self._align_inputparse_with_prefix, gene+postfix)
                fsl = FastaSeqList(bcg)
                fsl_len = fsl.get_seq_list_len()
                if fsl_len > 3:
                    #  TODO: seems like another tool support three or more sequences.
                    #  https://www.ebi.ac.uk/Tools/msa/clustalw2/
                    filtered_bcg.append(gene)
                    bcg_num += 1
                else:
                    #  TODO: use another tool to process pairwise gene alignment ?
                    #  https://en.wikipedia.org/wiki/List_of_sequence_alignment_software
                    LOGGER.info("Only three or fewer genomes have %s sequences."
                                "This gene is excluded in further analysis.", bcg)
                    # log about it here
            return filtered_bcg, bcg_num
        if self.config.align_mode == 'nt':
            self._bcg_filtered_in_align, self._bcg_num = filter_genomes_by_frequency(
                self.config.postfixes.input_parsing_dna_const)
        else:
            self._bcg_filtered_in_align, self._bcg_num = filter_genomes_by_frequency(
                self.config.postfixes.input_parsing_pro_const)
        for gene in self._bcg_filtered_in_align:
            LOGGER.info('Process alignment for %s', gene)
            self._genes_processed_with_mafft.append(self._mafft.run(gene))
        if self.config.align_mode in ('nt', 'aa'):
            for gene in self._genes_processed_with_mafft:
                LOGGER.info('Run gap fileting for %s', gene)
                self._filtering_gap_dna(gene)
        elif self.config.align_mode in ('codon', 'codon12'):
            for gene in self._genes_processed_with_mafft:
                LOGGER.info('Run gap fileting for %s', gene)
                dna_file, gene = self._filtering_gap_pro(gene)
                self._filtering_gap_dna((dna_file, gene))


    def _concatenating(self):
        """
        Method to concatenate aligned sequences
        :return:
        """
        LOGGER.info("Concatenating aligned UBCGs.")
        concatenated_fasta = []
        gene_length_map = {}
        gene_fasta_seq_list_map = {}
        for gene in self._bcg_filtered_in_align:
            file_name = os.path.join(self._align_filtering_output_with_prefix,
                                     gene+self.config.postfixes.align_align_const)
            fasta_seq_list = FastaSeqList(file_name) # var11
            if not all(len(fasta.seq) == fasta_seq_list.get_seq_len()
                       for fasta in fasta_seq_list.get_seq_list()):
                error = f'{file_name} has different sequence length.'
                LOGGER.error(error)
                raise ValueError(error)
            gene_length_map[gene] = fasta_seq_list.get_seq_len()
            gene_fasta_seq_list_map[gene] = fasta_seq_list

        # TODO check is bcg_list same as genomeList

        for seq_name in self._genome_name: # var19
            if concatenated_fasta:
                concatenated_fasta.append("\n>" + seq_name + "\n")
            else:
                concatenated_fasta.append(">" + seq_name + "\n")
            for fasta_list in gene_fasta_seq_list_map:
                if seq_name not in gene_fasta_seq_list_map[fasta_list].seq_list:
                    gaps = '-' * gene_length_map[fasta_list]
                    concatenated_fasta.append(gaps)
                else:
                    concatenated_fasta.append(
                        gene_fasta_seq_list_map[fasta_list].seq_list[seq_name].seq)
        output_file = os.path.join(
            self._align_alignment_output,
            self.config.align_mode + '_' + self.config.postfixes.align_concateneted)
        with open(output_file, 'w') as f:
            f.write(''.join(concatenated_fasta))


    def _filtering_gap_pro(self, data: tuple):
        """
        Method to process gap filtering for protein sequences after mafft
        :param data: tuple with path to sequence produced with mafft and gene name
        :return:
        """
        aligned_file = data[0]
        gene = data[1]
        dna_file = os.path.join(self._align_inputparse_with_prefix,
                                gene + self.config.postfixes.input_parsing_dna_const)
        LOGGER.info('Filter gaps for %s gene, aligned file %s, dna file %s',
                    gene, aligned_file, dna_file)
        fasta_dna_list = FastaSeqList(dna_file)
        aligned_protein = FastaSeqList(aligned_file)
        for fasta_seq in aligned_protein.get_seq_list():
            dna_fasta_seq = fasta_dna_list.seq_list[fasta_seq.title]
            aligned_seq = fasta_seq.seq
            dna_seq = dna_fasta_seq.seq
            for nuc_idx, nuc in enumerate(aligned_seq):
                if nuc == '-':
                    # TODO: Why x3 ?
                    insert_pos = 3 * nuc_idx
                    dna_seq = dna_seq[:insert_pos] + '---' + dna_seq[insert_pos:]
            #  specific to codon12 mode
            if self.config.align_mode == 'codon12':
                codon12 = ''
                for nuc_idx, nuc in enumerate(dna_seq):
                    if nuc_idx % 3 != 2:
                        codon12 += nuc
                dna_fasta_seq.seq = codon12
            else:
                dna_fasta_seq.seq = dna_seq
        file_path = os.path.join(
            self._align_align_with_prefix,
            gene+self.config.postfixes.align_align_const)
        fasta_dna_list.write_file(file_path)
        return file_path, gene


    def _filtering_gap_dna(self, data):
        """
        Method to process gap filtering for dna sequences after mafft
        :param file_path:
        :return:
        """
        aligned_file = data[0]
        gene = data[1]
        con_fasta_seq_list = FastaSeqList(aligned_file)
        # TODO: check if file not exist ?
        num_of_genes = con_fasta_seq_list.get_seq_list_len()
        LOGGER.info('Filter gaps for %s gene, aligned file %s', gene, aligned_file)
        seq_len = con_fasta_seq_list.get_seq_len()
        num_gaps = [0] * seq_len
        for fasta_seq in con_fasta_seq_list.get_seq_list():
            seq = fasta_seq.seq
            for nuc_idx, nuc in enumerate(seq):
                if nuc == '-':
                    num_gaps[nuc_idx] += 1
        for fasta_seq in con_fasta_seq_list.get_seq_list():
            seq = fasta_seq.seq
            temp_seq = ''
            for nuc_idx, nuc in enumerate(seq):
                if num_gaps[nuc_idx] <= num_of_genes * (1 - (self.config.filter / 100)):
                    temp_seq += nuc
            fasta_seq.seq = temp_seq
        # Aligner, line 1116
        output_path = os.path.join(self._align_filtering_output_with_prefix,
                                   gene+self.config.postfixes.align_align_const)
        con_fasta_seq_list.write_file(output_path)


    def _create_folder_if_not_exist(self, *args):
        """
        Create unique folder with given prefix
        :param args:
        :return: created dir path
        """
        path = os.path.join(self._dirpath, *args)
        if not os.path.exists(path):
            os.makedirs(path)
        return path
