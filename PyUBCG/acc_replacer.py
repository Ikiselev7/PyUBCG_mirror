# -*- coding: utf-8 -*-
"""
    This module replace labels in file string

"""
import logging

LOGGER = logging.getLogger('PyUBCG.acc_replace')


class ReplaceAcc:
    """
        Class to replace labels in file string
    """

    def __init__(self, replace_map, flag):
        self.replce_map = replace_map
        self._acc_list = []
        self._label_list = []
        self._acc_map = {}
        self._label_map = {}
        self._counter = 1
        self._flag = flag

    def add(self, acc, label):
        """
        Method to add label
        :param acc:
        :param label:
        :return: True
        """
        if acc in self._acc_list:
            LOGGER.warning('%s already exists.', acc)
            return False
        self._acc_map[acc] = len(self._acc_list)
        self._acc_list.append(acc)
        if label in self._label_map:
            label = label + '_' + str(self._counter)
            self._counter += 1
        self._label_map[label] = len(self._label_list)
        self._label_list.append(label)
        return True

    def replace(self, ori_str, is_newick=False):
        """
        Method replaces labels
        :param ori_str: file string
        :param is_newick: file format
        :return: string
        """
        res_str = ori_str
        for acc in range(len(self._acc_list)):
            if is_newick:
                label = self._label_list[acc].replace("'", "`")
                res = res_str.replace(self._flag + self._acc_list[acc] + self._flag, "'" + label + "'")
            else:
                res = res_str.replace(self._flag + self._acc_list[acc] + self._flag, self._label_list[acc])
        return res
