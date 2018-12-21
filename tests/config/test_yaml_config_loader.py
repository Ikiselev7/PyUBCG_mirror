from unittest import mock
from src.config_loader_yaml import ConfigLoaderYaml


def test_yaml_config():
    with mock.patch('builtins.open', return_value=open('tests/config/files/test_config.yaml')):
        config = ConfigLoaderYaml('test')
        assert config.param1 == 'value'
        assert config.project_name == 'PyUBCG'