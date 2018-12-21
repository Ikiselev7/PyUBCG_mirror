import yaml
import argparse

from src.ABC_config_loader import ConfigLoaderABC


class ConfigLoaderYaml(ConfigLoaderABC):

    @staticmethod
    def load_config(path):
        with open(path) as yaml_conf:
            config = yaml.load(yaml_conf)

        # To run program with arguments from command line
        # probably i should place it in another place, like __main__.py
        # and pass it like argument to this function
        parser = argparse.ArgumentParser(description='app')
        parser.add_argument('--project_name', default='PyUBCG')
        args = parser.parse_args()
        for key, value in args.__dict__.items():
            config[key] = value
        return config
