import json
import re
import os

from .core import stdClass
from _include import loader
PATH_PROJECT = loader("PATH_PROJECT", "")

PATH_APP = os.path.join(PATH_PROJECT, 'websrc', 'app')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_MODULES = os.path.join(PATH_WEBSRC, 'modules')

class config(stdClass):
    def __init__(self, name='config', data=stdClass()):
        self.data = data
        self.name = name

    @classmethod
    def load(self, name='config'):
        c = config()
        config_path = os.path.join(PATH_APP, 'config', name + '.py')
        if os.path.isfile(config_path) == False:
            c.data = dict()

        try:
            with open(config_path, mode="r") as file:
                _tmp = {'config': None}
                _code = file.read()
                exec(_code, _tmp)
                c.data = _tmp['config']
        except Exception as e:
            pass

        return c

    def get(self, key=None, _default=None):
        if key is None:
            return self.data
        if key in self.data:
            return self.data[key]
        return _default
