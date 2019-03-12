# -*- coding: utf-8 -*-

import pytest
import json
from PyUBCG.bcg_dto import BcgDto, BcgGenData, BcgDtoEncoder

# test empty
input_1 = ("1550089557386", "CP012646_s KCOM 1350", "GCA_001281025.1",
           "CP012646_s", None, "KCOM 1350", None, None, None, 92, "v3.0", 92,
           92, 0,
           BcgGenData("rpmC", 0, {}),
           BcgGenData("recA", 0, {}))
expected_1 = 'tests/bcg_files/1-test.json'

# test with data
input_2 = ("1550089557386", "CP012646_s KCOM 1350", "GCA_001281025.1",
           "CP012646_s", None, "KCOM 1350", None, None, None, 92, "v3.0", 92,
           92, 0,
           BcgGenData("recA", 1,
                      {"feature_index": 582, "dna": "ACTCTTGACCTAGGCGATGAGC",
                       "protein": "LDLGDELEIEIEEGCGATGAGC",
                       "evalue": "8.3E-162"}),
           BcgGenData("rpmC", 4,
                      {"feature_index": 522, "dna": "ATGAAACTTAATGAAGTAAAAG",
                       "protein": "MKLNEVKEFVKELRGLSQEELA",
                       "evalue": "2.4E-24"},
                      {"feature_index": 522, "dna": "ATGAAACTTAATGAAGTAAAAG",
                       "protein": "MKLNEVKEFVKELRGLSQEELA",
                       "evalue": "2.4E-24"},
                      {"feature_index": 522, "dna": "ATGAAACTTAATGAAGTAAAAG",
                       "protein": "MKLNEVKEFVKELRGLSQEELA",
                       "evalue": "2.4E-24"},
                      {"feature_index": 522, "dna": "ATGAAACTTAATGAAGTAAAAG",
                       "protein": "MKLNEVKEFVKELRGLSQEELA",
                       "evalue": "2.4E-24"}))
expected_2 = 'tests/bcg_files/2-test.json'


@pytest.mark.parametrize('uid,label,accession,taxon_name,ncbi_name,strain_name,\
                         strain_type,strain_property,taxonomy,\
                         UBCG_target_gene_number,version,n_ubcg,n_genes,\
                         n_paralog_ubcg,d1,d2,expected',
                         [pytest.param(*input_1, expected_1),
                          pytest.param(*input_2, expected_2)])
def test_bcg(capsys, uid, label, accession, taxon_name, ncbi_name,
             strain_name, strain_type, strain_property, taxonomy,
             UBCG_target_gene_number, version, n_ubcg, n_genes,
             n_paralog_ubcg, d1, d2, expected):
    bcg_dto = BcgDto(uid, label, accession, taxon_name, ncbi_name, strain_name,
                     strain_type, strain_property, taxonomy,
                     UBCG_target_gene_number, version, n_ubcg, n_genes,
                     n_paralog_ubcg, d1, d2)

    json_data = json.dumps(bcg_dto, cls=BcgDtoEncoder)

    # according to bcg format
    dict_list = json.loads(json_data)
    # make list of json strs
    str_list = []
    for val in dict_list:
        str_list.append(json.dumps(val))

    with open(expected) as file:
        test_dict_list = json.load(file)
        # make list of json strs
        test_str_list = []
        for val in test_dict_list:
            test_str_list.append(json.dumps(val))

        # compare 2 sets
        assert set(str_list) == set(test_str_list)
