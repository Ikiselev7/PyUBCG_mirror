import os

from PyUBCG.acc_replacer import ReplaceAcc


class LabelReplacer:

    def __init__(self, config, replace_map):
        self._flag = config.postfixes.align_flag
        self.replace_map = replace_map

    def replace_name(self, input_file, output_file, delete=False):
        ori_str = self._read_rext_file_to_str(input_file)
        new_str = self._replace_name_str(ori_str)
        if delete:
            try:
                os.remove(input_file)
            except Exception as e:
                ...
        with open(output_file, 'w') as ouf_file:
            ouf_file.write(new_str)

    def _replace_name_str(self, ori_str):
        nodes = ori_str.split(self._flag)
        acc_repl = ReplaceAcc(self.replace_map, self._flag)
        for i in range(1, len(nodes), 2):
            uid = nodes[i]
            label = self.replace_map[uid]
            acc_repl.add(uid, label)
        return acc_repl.replace(ori_str, is_newick=True)

    # For now its okay but probably for large files its not a best way
    def _read_rext_file_to_str(self, filename):
        with open(filename, 'r') as file:
            return ''.join(i for i in file.readlines())
