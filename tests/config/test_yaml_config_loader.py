import shutil
from unittest import mock
import pytest
from PyUBCG.config_loader_yaml import ConfigLoaderYaml
from PyUBCG.app import Main


@pytest.fixture
def main_object():
    with mock.patch('shutil.which', return_value=True):
        return Main(config='tests/config/files/test_config.yaml', input_folder='fasta_input/')


def test_yaml_config(main_object):
    config = main_object._config
    assert config['paths']['fasta_input_folder'] == 'fasta_input'
