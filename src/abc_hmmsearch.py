# -*- coding: utf-8 -*-
"""
    This module provide hmmsearch ABC class to instantiate wrapper

"""


from src.abc_program_wrapper import UtilWrapperABC

class HmmsearchABC(UtilWrapperABC):
    """
    Hmmsearch wrapper class
    """

    def __new__(cls, config):
        tool_type = config.hmmsearch_like_tool
        if tool_type == 'hmmsearch':
            from src.hmmsearch_wrapper import Hmmsearch
            _impl = Hmmsearch
        return super(HmmsearchABC, cls).__new__(_impl)

    def run(self, file_path: str, **kwargs):
        raise NotImplementedError
