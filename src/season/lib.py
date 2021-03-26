import json
import re
import os

from .core import stdClass

from _include import loader
PATH_PROJECT = loader("PATH_PROJECT", "")
PATH_APP = os.path.join(PATH_PROJECT, 'websrc', 'app')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_MODULES = os.path.join(PATH_WEBSRC, 'modules')

class lib(stdClass):
    def __init__(self, framework):
        self.framework = framework
        self._cache = stdClass()

    def __getattr__(self, attr):
        if attr in self._cache:
            return self._cache[attr]

        libpath = os.path.join(PATH_MODULES, self.framework._modulename,'lib', attr + '.py')
        if os.path.isfile(libpath):
            f = open(libpath, 'r')
            _code = f.read()
            f.close()

            _tmp = stdClass()
            exec(_code, _tmp)
            obj = _tmp
            self._cache[attr] = obj
            return obj

        libpath = os.path.join(PATH_APP, 'lib', attr + '.py')
        if os.path.isfile(libpath):
            f = open(libpath, 'r')
            _code = f.read()
            f.close()

            _tmp = stdClass()
            exec(_code, _tmp)
            obj = _tmp
            self._cache[attr] = obj
            return obj

        if hasattr(core, attr):
            fn = getattr(core, attr)
            obj = fn(self.framework)
            self._cache[attr] = obj
            return obj
        
        return stdClass()

class core(stdClass):
    class session:
        def __init__(self, framework):
            self.framework = framework
            self.flask = framework.flask

        def has(self, key):
            if key in self.flask.seasion:
                return True
            return False
        
        def delete(self, key):
            self.flask.session.pop(key)

        def set(self, key, value):
            self.flask.session[key] = value

        def get(self, key, default=None):
            if key in self.flask.session:
                return self.flask.session[key]
            return default

        def clear(self):
            self.flask.session.clear()

        def to_dict(self):
            return dict(self.flask.session)

            