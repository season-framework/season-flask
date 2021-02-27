import json
import re
import os

from .core import stdClass

from _include import loader
PATH_PROJECT = loader("PATH_PROJECT", "")
PATH_APP = os.path.join(PATH_PROJECT, 'season-flask', 'public', 'websrc', 'app')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_MODULES = os.path.join(PATH_WEBSRC, 'modules')

class lib(stdClass):
    def __init__(self, framework):
        self.framework = framework
        self._cache = stdClass()

    def __getattr__(self, attr):
        if attr in self._cache:
            return self._cache[attr]

        codepath = os.path.join(PATH_PROJECT, 'season-flask', 'framework', 'season', 'code', 'lib.py')
        libpath = os.path.join(PATH_APP, 'lib', attr + '.py')
        if os.path.isfile(libpath):
            f = open(codepath, 'r')
            prefix = f.read()
            f.close()

            f = open(libpath, 'r')
            _code = f.read()
            f.close()

            _code = prefix + '\n' + _code
            _tmp = stdClass()
            exec(_code, _tmp)

            obj = getattr(_tmp, '__base__')(self.framework, _tmp)
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
            print('pre', self.to_dict())
            self.flask.session.clear()
            print('next', self.to_dict())

        def to_dict(self):
            return dict(self.flask.session)

            