"""
    Wrapper to call docker container with preinstalled transdecoder and
    process gene prediction.
"""

import os
import shutil
import stat


import docker

from PyUBCG.abc import AbstractProdigal


PROG_POSTFIX = '.transdecoder_dir'


class Transdecoder(AbstractProdigal):
    """
        Wrapper to run Transdecoder
    """
    def __init__(self, config):
        self._config = config
        self._dirpath = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
        self._input_path = os.path.join(*(self._dirpath, config['paths']['fasta_input_folder']))
        self._gene_pro_path = os.path.join(*(self._dirpath,
                                             config['paths']['prodigal_output'],
                                             config['prefixes']['pro_prefix']
                                             ))
        self._gene_nuc_path = os.path.join(*(self._dirpath,
                                             config['paths']['prodigal_output'],
                                             config['prefixes']['nuc_prefix']
                                             ))


    def run(self, file_name: str, *args, **kwargs):
        """
        Method to execute gene prediction by transdecoder.
        :param file_name:
        :param args:
        :param kwargs:
        :return:
        """
        cli = docker.from_env()
        tmp_folder = self._input_path +'/' + file_name + '_tmp_dir'
        os.mkdir(tmp_folder)
        shutil.copyfile(self._input_path +'/' + file_name, tmp_folder)
        volume = {tmp_folder: {'bind': '/run_dir', 'mode': 'rw'}}
        command = ['TransDecoder.LongOrfs', '-t', file_name]
        cli.containers.run('comics/transdecoder', volumes=volume, working_dir='/run_dir', command=command, auto_remove=True)
        self._extract_results(file_name, tmp_folder)


    def _extract_results(self, file_name, tmp_folder):
        """
        Extract cds and pep file from folder created by transdecoder and place
        it ti right place.
        :param file_name:
        :return:
        """
        folder_path = os.path.join(tmp_folder, file_name+PROG_POSTFIX)
        files = os.listdir(folder_path)
        pep, cds = [file for file in files if file.split('.')[-1] in ('pep', 'cds')]
        os.chmod(folder_path+'/'+pep, stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
        os.chmod(folder_path+'/'+cds, stat.S_IROTH | stat.S_IWOTH | stat.S_IXOTH)
        shutil.copyfile(folder_path+'/'+pep, os.path.join(self._gene_pro_path, file_name))
        shutil.copyfile(folder_path+'/'+cds, os.path.join(self._gene_nuc_path, file_name))
        shutil.rmtree(tmp_folder)
