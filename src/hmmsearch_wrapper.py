# -*- coding: utf-8 -*-
"""
    ACB wrapper to hmmsearch-like program

"""

from src.abc_program_wrapper import UtilWrapperABC


class Hmmsearch(UtilWrapperABC):
    """
    Wrapper to hmmsearch
    """

    def run(self, file_path: str, **kwargs) -> None:
        """
        Method to execute hmmsearch
        :param path: some file here
        :kwargs: args to run program with
        :return:
        """
