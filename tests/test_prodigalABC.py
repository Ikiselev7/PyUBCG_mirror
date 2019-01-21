import pytest
import shutil
import builtins
import argparse
import subprocess
from unittest import mock
from PyUBCG.app import Main



@pytest.fixture
def prodigal_object():
    with mock.patch('argparse.ArgumentParser.parse_args',
                    return_value=argparse.Namespace(
                        config='config/config.yaml',
                        input_folder='fasta_input/')):
        with mock.patch('shutil.which', return_value=True):
            with mock.patch('builtins.open', return_value=open('tests/config/files/test_config.yaml')):
                return Main()._prodigal

class MockedPopen:

    def __init__(self, args, **kwargs):
        self.args = args
        self.returncode = 0

    def __enter__(self):
        return self

    def __exit__(self, exc_type, value, traceback):
        pass

    def wait(self):
        if self.args[0] == 'prodigal -i some_file -a pro -d nuc':
            stdout = 'done'
            stderr = ''
            self.returncode = 0
        else:
            stdout = ''
            stderr = 'unknown command'
            self.returncode = 1

        return self.returncode


def test_prodigal_setup(prodigal_object):
    assert prodigal_object._project_dir == 'PyUBCG'

@mock.patch('subprocess.Popen', MockedPopen)
def test_run_method(prodigal_object):
    with subprocess.Popen(['prodigal -i some_file -a pro -d nuc']) as proc:
        assert proc.wait() == 0