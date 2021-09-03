import os
import datetime
import shutil

from .util.bootstrap import bootstrap
from .util.stdclass import stdClass

from .framework.request import request
from .framework.segment import segment
from .framework.response import response
from .framework.lib import lib
from .framework.status import status

LOG_DEBUG = 0
LOG_INFO = 1
LOG_DEV = 2
LOG_WARNING = 3
LOG_ERROR = 4
LOG_CRITICAL = 5

core = stdClass()
core.PATH = stdClass()
core.PATH.FRAMEWORK = os.path.dirname(__file__)
core.PATH.PROJECT = os.path.join(os.getcwd())
core.PATH.PUBLIC = os.path.join(core.PATH.PROJECT, 'public')
core.PATH.WEBSRC = os.path.join(core.PATH.PROJECT, 'websrc')
core.PATH.TEMPLATE = os.path.join(core.PATH.PUBLIC, 'templates')
core.PATH.APP = os.path.join(core.PATH.WEBSRC, 'app')
core.PATH.MODULES = os.path.join(core.PATH.WEBSRC, 'modules')

core.CLASS = stdClass()
core.CLASS.REQUEST = request
core.CLASS.SEGMENT = segment
core.CLASS.RESPONSE = response
core.CLASS.LIB = lib
core.CLASS.RESPONSE.STATUS = status

interfaces = stdClass()

class config(stdClass):
    def __init__(self, name='config', data=stdClass()):
        self.data = data
        self.name = name

    @classmethod
    def load(self, name='config'):
        c = config()
        config_path = os.path.join(core.PATH.APP, 'config', name + '.py')
        if os.path.isfile(config_path) == False:
            c.data = dict()

        try:
            with open(config_path, mode="rb") as file:
                _tmp = {'config': None}
                _code = file.read().decode('utf-8')
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

def build_template():
    try:
        shutil.rmtree(core.PATH.TEMPLATE)
    except:
        pass

    try:
        os.makedirs(core.PATH.TEMPLATE, exist_ok=True)
    except:
        pass

    def find_viewpath(directory):
        paths = []
        for (path, _, filenames) in os.walk(directory):
            viewpath = os.path.join(path, "view")
            if os.path.isdir(viewpath):
                paths.append(viewpath)
        return paths

    viewpaths = find_viewpath(core.PATH.MODULES)
    for viewpath in viewpaths:
        if os.path.isdir(viewpath) == False: continue
        module = viewpath[len(core.PATH.MODULES)+1:-5]
        targetpath = os.path.join(core.PATH.TEMPLATE, module)
        try:
            os.makedirs(os.path.dirname(targetpath), exist_ok=True)
        except:
            pass
        try:
            os.symlink(viewpath, targetpath)
        except:
            pass

core.build = stdClass()
core.build.template = build_template

# json_default
def json_default(value): 
    if isinstance(value, datetime.date): 
        return value.strftime('%Y-%m-%d %H:%M:%S') 
    raise str(value)

core.json_default = json_default    

# interfaces
class _interfaces(dict):
    def __init__(self, namespace="interfaces"):
        super(_interfaces, self).__init__()
        self.__NAMESPACE__ = namespace

    def __getattr__(self, attr):
        NAMESPACE = ".".join([self.__NAMESPACE__, attr])
        FUNCNAME = NAMESPACE.split(".")[-1]

        def load_interface(FILEPATH):
            if os.path.isfile(FILEPATH):
                file = open(FILEPATH, mode="rb")
                _tmp = stdClass()
                _tmp['__file__'] = FILEPATH
                _code = file.read().decode('utf-8')
                file.close()
                exec(compile(_code, FILEPATH, 'exec'), _tmp)
                if FUNCNAME in _tmp:
                    return _tmp[FUNCNAME]
            return None

        # module interfaces
        path = NAMESPACE.split(".")[:-1]
        path = path[1:]
        for i in range(len(path)):
            idx = len(path) - i
            module = "/".join(path[:idx])
            module_path = os.path.join(core.PATH.MODULES, module)
            interface_path = "/".join(path[idx:]) + ".py"
            FILEPATH = os.path.join(module_path, "interfaces", interface_path)
            interface = load_interface(FILEPATH)
            if interface is not None: 
                return interface

        # global interfaces
        FILEPATH = os.path.join(core.PATH.APP, "/".join(NAMESPACE.split(".")[:-1])) + ".py"
        interface = load_interface(FILEPATH)
        if interface is not None: 
            return interface
    
        return _interfaces(NAMESPACE)

interfaces = _interfaces()

# core interfaces
class _interfacesc(dict):
    def __init__(self, namespace="interfaces"):
        super(_interfacesc, self).__init__()
        self.__NAMESPACE__ = namespace

    def __getattr__(self, attr):
        NAMESPACE = ".".join([self.__NAMESPACE__, attr])
        FILEPATH = os.path.join(core.PATH.FRAMEWORK, 'framework', "/".join(NAMESPACE.split(".")[:-1])) + ".py"
        FUNCNAME = NAMESPACE.split(".")[-1]

        if os.path.isfile(FILEPATH):
            file = open(FILEPATH, mode="rb")
            _tmp = stdClass()
            _tmp['__file__'] = FILEPATH
            _code = file.read().decode('utf-8')
            file.close()
            exec(compile(_code, FILEPATH, 'exec'), _tmp)

            if FUNCNAME in _tmp:
                return _tmp[FUNCNAME]

        return _interfacesc(NAMESPACE)

core.interfaces = _interfacesc()

if os.path.isdir(core.PATH.WEBSRC):
    framework = stdClass()
    framework.core = core
    framework.interfaces = interfaces
    framework.config = config

    bootstrap = bootstrap(framework).bootstrap