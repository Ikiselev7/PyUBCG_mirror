import pytest
import shutil
import builtins
import argparse
from unittest import mock
from PyUBCG.app import Main



@pytest.fixture
def main_object():
    with mock.patch('argparse.ArgumentParser.parse_args',
                    return_value=argparse.Namespace(
                        config='config/config.yaml',
                        input_folder='fasta_input/')):
        with mock.patch('shutil.which', return_value=True):
            with mock.patch('builtins.open', return_value=open('tests/config/files/test_config.yaml')):
                return Main()


def test_config_load_in_main(main_object):
    assert main_object._config.param1 == 'value'
    assert main_object._config.project_name == 'PyUBCG'

def test_prodigal_like_tool_presence(main_object):
    assert main_object._prodigal.__class__.__name__ == 'Prodigal'

def test_hmmsearch_like_tool_presence(main_object):
    assert main_object._hmmsearch.__class__.__name__ == 'Hmmsearch'


