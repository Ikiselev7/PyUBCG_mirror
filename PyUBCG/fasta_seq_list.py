# -*- coding: utf-8 -*-
"""
    This module hold object representation of multiple fasta file

"""

import logging

from PyUBCG.fasta_seq import FastaSeq

LOGGER = logging.getLogger('PyUBCG.FastaSeqList')

class FastaSeqList:
    """
    Class to hold all single fasta records
    """
    def __init__(self, file_name):
        self.seq_list = {}
        self.file_name = file_name
        self.parse_file()


    def get_seq_list_len(self) -> int:
        """
        Method to get amount of fasta objects in list
        :return:
        """
        return len(self.seq_list)


    def parse_file(self):
        """
        Method to parse multiple-fasta file and create object representation of
        single fasta file
        :return:
        """
        is_first = True
        is_first_line_found = False
        temp_seq = ''
        temp_title = ''
        with open(self.file_name) as fasta_file:
            # file = fasta_file.readlines()
            print(self.file_name)
            # pprint(file)
            # sys.exit()
            for line in fasta_file:
                if is_first and not line.startswith('>'):
                    temp_seq = temp_seq + line.strip()
                    is_first = False
                    is_first_line_found = True
                elif line[0] not in ('>', '#') and is_first_line_found:
                    temp_seq = temp_seq + line.strip()
                elif is_first:
                    is_first = False
                    temp_title = line[1:].strip()
                    is_first_line_found = True
                else:
                    temp_seq = temp_seq.upper()
                    self.add_seq(temp_title, temp_seq)
                    temp_title = line[1:].strip()
                    temp_seq = ''
            if temp_seq:
                self.add_seq(temp_title, temp_seq)

    def get_seq_len(self):
        """
        Get length of sequence in single fasta obj
        We assume that they all have same length
        :return:
        """
        return len(list(self.seq_list.values())[0].seq)

    def add_seq(self, title, seq):
        """
        Method to create FastaSeq instance and add int to object map
        :param title:
        :param seq:
        :return:
        """
        # 1 is hardcoded in origin
        # LOGGER.info('Create FastaSeq obj with %s title', title)
        fasta_seq = FastaSeq(title, seq, 1)
        self.seq_list[title] = fasta_seq



    def get_seq_list(self):
        """
        Method to get list of instances inside obj map
        :return:
        """
        return list(self.seq_list.values())

    def write_file(self, path):
        """
        Method to write and concatenate all instances sequences inside map
        :param path:
        :return:
        """
        with open(path, 'w') as file:
            for seq in self.seq_list:
                title = self.seq_list[seq].title
                seq = self.seq_list[seq].seq
                file.write('>'+title+'\n'+seq+'\n')

    def __getattr__(self, item):
        return self.seq_list[item]


