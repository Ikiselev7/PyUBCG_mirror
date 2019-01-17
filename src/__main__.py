# -*- coding: utf-8 -*-
"""PyUBCG
Entry point to module

"""

from src.main import Main

APP = Main()
APP.extract()
# APP._process_hmm_output_to_json('CP012646_s_GCA_001281025.1_KCOM_1350.fasta')
# APP.run()
