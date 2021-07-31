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

if os.path.isdir(core.PATH.WEBSRC):
    # json_default
    def json_default(value): 
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S') 
        raise str(value)

    core.json_default = json_default

    # interface loader
    def _build_interface(obj, keys, instname, inst, lv=0):
        if len(keys) == 0 and obj is not None:
            bname = os.path.splitext(os.path.basename(instname))[0]
            obj[bname] = inst
            return obj

        if lv >= len(keys):
            bname = os.path.splitext(os.path.basename(instname))[0]
            if obj is not None: _obj = obj
            else: _obj = stdClass()
            _obj[bname] = inst
            return _obj

        if obj is None: obj = stdClass()
        key = keys[lv]

        if key in obj:
            obj[key] = _build_interface(obj[key], keys, instname, inst, lv=lv+1)
        else: 
            obj[key] = _build_interface(None, keys, instname, inst, lv=lv+1)

        return obj

    # load package defined interface, season.core.interfaces.*
    core.interfaces = stdClass()
    interfaces_dir = os.path.join(core.PATH.FRAMEWORK, 'framework', 'interfaces')
    for dirpath, dirname, interfacenames in os.walk(interfaces_dir):
        if len(interfacenames) == 0: continue
        _dir = dirpath[len(interfaces_dir) + 1:]
        if len(_dir) == 0:
            _dir = []
        else:
            _dir = _dir.split('/')
        
        for interfacename in interfacenames:
            _, ext = os.path.splitext(interfacename)
            if ext != '.py': continue
            _class = os.path.join(dirpath, interfacename)
            file = open(_class, mode="rb")
            _tmp = stdClass()
            _tmp['__file__'] = _class
            _code = file.read().decode('utf-8')
            file.close()
            exec(compile(_code, _class, 'exec'), _tmp)
            _build_interface(core.interfaces, _dir, interfacename, _tmp)

    # load user defined interface: season.interfaces.*
    interfaces_dir = os.path.join(core.PATH.APP, 'interfaces')
    for dirpath, dirname, interfacenames in os.walk(interfaces_dir):
        if len(interfacenames) == 0: continue
        _dir = dirpath[len(interfaces_dir) + 1:]
        if len(_dir) == 0:
            _dir = []
        else:
            _dir = _dir.split('/')
        
        for interfacename in interfacenames:
            _, ext = os.path.splitext(interfacename)
            if ext != '.py': continue
            _class = os.path.join(dirpath, interfacename)
            file = open(_class, mode="rb")
            _tmp = stdClass()
            _tmp['__file__'] = _class
            _code = file.read().decode('utf-8')
            file.close()
            exec(compile(_code, _class, 'exec'), _tmp)
            _build_interface(interfaces, _dir, interfacename, _tmp)

    # load config
    framework = stdClass()
    framework.core = core
    framework.interfaces = interfaces
    framework.config = config

    bootstrap = bootstrap(framework).bootstrap