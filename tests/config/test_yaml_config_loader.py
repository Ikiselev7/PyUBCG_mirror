import shutil
from unittest import mock
import pytest
from PyUBCG.config_loader_yaml import AbstractConfigLoaderYaml
from PyUBCG.app import Main


@pytest.fixture
def main_object():
    with mock.patch('shutil.which', return_value=True):
        return Main(config='tests/config/files/test_config.yaml', input_folder='fasta_input/')


def test_yaml_config(main_object):
    with mock.patch('builtins.open', return_value=open('tests/config/files/test_config.yaml')):
        config = AbstractConfigLoaderYaml(main_object._args)
        assert config.param1 == 'value'
        assert config.input_folder == 'fasta_input/'
