# -*- coding: utf-8 -*-
"""
    DTO class for BCG format file with json encoder

"""

import json


class BcgDtoEncoder(json.JSONEncoder):
    """
    Encoder class for BcgDto
    """
    def default(self, o):  # pylint: disable=E0202
        if isinstance(o, _BcgGenDataStruct):
            return {o.name: [o.n_genes, o.genes]}
        if isinstance(o, BcgGenData):
            if o.n_genes == 0:
                return [0]
            res = [o.n_genes]
            data_struct = _BcgGenDataStruct()
            for r in o.genes:
                res.append([r[key] for key in data_struct.genes])
            return res
        if isinstance(o, _BcgGenDataWrapper):
            d = {}
            for val in o.genes_list:
                d[val.name] = val
            return d
        if isinstance(o, BcgDto):
            res_dict = _join_target_gene_number_with_version(o)
            result = []
            for attr, value in res_dict.items():
                result.append({attr: value})
            return result

        return json.JSONEncoder.default(self, o)


class BcgDto():  # pylint: disable=R0902
    """
    Class to store all metadata from bcg json file
    """
    def __init__(self, uid, label, accession,  # pylint: disable=R0913, R0914,
                 taxon_name, ncbi_name, strain_name, strain_type,
                 strain_property, taxonomy, UBCG_target_gene_number, version,
                 n_ubcg, n_genes, n_paralog_ubcg, *args):
        self.uid = uid
        self.label = label
        self.accession = accession
        self.taxon_name = taxon_name
        self.ncbi_name = ncbi_name
        self.strain_name = strain_name
        self.strain_type = strain_type
        self.strain_property = strain_property
        self.taxonomy = taxonomy
        self.UBCG_target_gene_number = UBCG_target_gene_number
        self.version = version
        self.n_ubcg = n_ubcg
        self.n_genes = n_genes
        self.n_paralog_ubcg = n_paralog_ubcg
        self.data_structure = _BcgGenDataStruct()
        self.data = _BcgGenDataWrapper(args)


class _BcgGenDataStruct:
    """
    Class to store gene metadata from bcg json file
    """
    def __init__(self):
        self.name = "gene_name"
        self.n_genes = "n_genes"
        self.genes = ["feature_index", "dna", "protein", "evalue"]


class BcgGenData:
    """
    Class to store gene data from bcg json file
    """
    def __init__(self, name, n_genes, *args):
        self.name = name
        self.n_genes = n_genes
        self.genes = list(args)


class _BcgGenDataWrapper:
    """
    Class-wrapper for BcgGenDataStruct and BcgGenData classes
    """
    def __init__(self, args):
        try:
            # try to cast to list (if tuple)
            self.genes_list = list(args)
        except TypeError:
            # define new list
            self.genes_list = [args]


def _join_target_gene_number_with_version(bcg_dto):
    bcg_dto_dict = bcg_dto.__dict__.copy()
    attrs = ('UBCG_target_gene_number', 'version')
    values = [bcg_dto_dict.pop(attr) for attr in attrs]
    bcg_dto_dict['{}|{}'.format(
        attrs[0], attrs[1])] = '{}|{}'.format(values[0], values[1])

    return bcg_dto_dict
