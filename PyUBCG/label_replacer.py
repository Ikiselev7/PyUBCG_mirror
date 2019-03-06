# -*- coding: utf-8 -*-
"""
    This module process replace labels for output files

"""

import os

from PyUBCG.acc_replacer import ReplaceAcc


class LabelReplacer:
    """
        Class to process replace labels
    """

    def __init__(self, config, replace_map):
        self._flag = config.postfixes.align_flag
        self.replace_map = replace_map

    def replace_name(self, input_file, output_file, delete=False):
        """
        Method to replace label in input file
        :param input_file: input file for replace
        :param output_file: expected output file
        :param delete: True if need to delete input file
        :return:
        """
        ori_str = self._read_rext_file_to_str(input_file)
        new_str = self._replace_name_str(ori_str)
        if delete:
            try:
                os.remove(input_file)
            except OSError:
                ...
        with open(output_file, 'w') as ouf_file:
            ouf_file.write(new_str)

    def _replace_name_str(self, ori_str):
        """
        Method to replace label in file string
        :param ori_str: file string
        :return: replaced string
        """
        nodes = ori_str.split(self._flag)
        acc_repl = ReplaceAcc(self.replace_map, self._flag)
        for i in range(1, len(nodes), 2):
            uid = nodes[i]
            label = self.replace_map[uid]
            acc_repl.add(uid, label)
        return acc_repl.replace(ori_str, is_newick=True)

    # For now its okay but probably for large files its not a best way
    @staticmethod
    def _read_rext_file_to_str(filename):
        with open(filename, 'r') as file:
            return ''.join(i for i in file.readlines())
