import pytest
import argparse
import shutil
from unittest import mock
from src.config_loader_yaml import ConfigLoaderYaml
from src.main import Main



@pytest.fixture
def main_object():
    with mock.patch('argparse.ArgumentParser.parse_args',
                    return_value=argparse.Namespace(
                        config='config/config.yaml',
                        input_folder='fasta_input/')):
        with mock.patch('shutil.which', return_value=True):
            return Main()


def test_yaml_config(main_object):
    with mock.patch('builtins.open', return_value=open('tests/config/files/test_config.yaml')):
        config = ConfigLoaderYaml(main_object._args)
        assert config.param1 == 'value'
        assert config.input_folder == 'fasta_input/'
