# -*- coding: utf-8 -*-
"""
    This module hold object representation of fasta file with single genome

"""


class FastaSeq:
    """
    Object to hold fasta file fata
    """
    def __init__(self, title, seq, number_added_seq):
        self.title = title
        self.seq = seq
        #  what fore here it is not clear from origin
        self.number_added_aeq = number_added_seq
        self.acc = ''


