import abc
import sys

class ConfigLoaderABC(abc.ABC):

    def __init__(self, path):
        self.config = self.load_config(path)

    @staticmethod
    @abc.abstractmethod
    def load_config(path):
        pass

    def __getattr__(self, item: str):
        if item not in self.config:
            raise KeyError('Value not in config')
        return self.config[item]