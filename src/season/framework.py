import json
import re
import os

from flask import session

from _include import loader
from .core import stdClass

from .response import response
from .request import request
from .segment import segment
from .config import config
from .lib import lib

PATH_PROJECT = loader("PATH_PROJECT", "")
PATH_APP = os.path.join(PATH_PROJECT, 'websrc', 'app')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_MODULES = os.path.join(PATH_WEBSRC, 'modules')

class framework:
    def __init__(self, flask, modulename, segmentpath):
        self.flask = flask
        self._modulename = modulename
        self._segmentpath = segmentpath
        self._cache = stdClass()
        self._cache.model = stdClass()

    @classmethod
    def load(self, flask, modulename, segmentpath):
        fr = framework(flask, modulename, segmentpath)
        fr.request = request(flask)
        fr.request.segment = segment(fr)
        fr.response = response(flask, modulename)
        fr.config = config
        fr.lib = lib(fr)

        fr.response.data.set(module=modulename)

        def model(modelname, module=modulename):
            model_path = None
            if module is not None:
                model_path = os.path.join(PATH_MODULES, module, 'model', modelname + '.py')

                if os.path.isfile(model_path) == False:
                    model_path = os.path.join(PATH_APP, 'model', modelname + '.py')
            else:
                model_path = os.path.join(PATH_APP, 'model', modelname + '.py')

            if model_path in fr._cache.model:
                return fr._cache.model[model_path]
            
            if os.path.isfile(model_path) == False:
                fr.response.error(500, 'Model Not Found')

            with open(model_path, mode="r") as file:
                _tmp = {'Model': None}
                _code = file.read()
                exec(_code, _tmp)
                fr._cache.model[model_path] = _tmp['Model'](fr)
                return fr._cache.model[model_path]

        fr.model = model
        return fr
