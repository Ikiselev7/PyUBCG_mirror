import pytest
from unittest import mock

from PyUBCG.app import Main


@pytest.fixture
def main_object():
    with mock.patch('shutil.which', return_value=True):
        return Main(config='tests/config/files/test_config.yaml', input_folder='fasta_input/', command='extract', )


def test_yaml_config(main_object):
    config = main_object._config
    assert config['paths']['fasta_input_folder'] == 'fasta_input'
