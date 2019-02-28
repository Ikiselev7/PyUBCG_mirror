import shutil
import builtins
from unittest import mock
import pytest

from PyUBCG.app import Main


@pytest.fixture
def main_object():
    with mock.patch('shutil.which', return_value=True):
        return Main(config='tests/config/files/test_config.yaml', input_folder='fasta_input/')


def test_config_load_in_main(main_object):
    assert main_object._config['general']['project_name'] == 'PyUBCG'
    assert main_object._config['paths']['fasta_input_folder'] == 'fasta_input'


def test_prodigal_like_tool_presence(main_object):
    assert main_object._prodigal.__class__.__name__ == 'Prodigal'


def test_hmmsearch_like_tool_presence(main_object):
    assert main_object._hmmsearch.__class__.__name__ == 'Hmmsearch'


