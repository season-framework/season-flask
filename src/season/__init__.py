import os
import datetime
import shutil
import json

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
cache = stdClass()

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

    def __getitem__(self, key):
        return self.__getattr__(key)

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

    def __getitem__(self, key):
        return self.__getattr__(key)

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

# dictionary
class dicObjClass(dict):
    def __init__(self, *args, **kwargs):
        super(dicObjClass, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.items():
                    if isinstance(v, dict):
                        self[k] = dicObjClass(v)
                    else:
                        self[k] = v

        if kwargs:
            for k, v in kwargs.items():
                if isinstance(v, dict):
                    self[k] = dicObjClass(v)
                else:
                    self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(dicObjClass, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(dicObjClass, self).__delitem__(key)
        del self.__dict__[key]

def __finddic__():
    mydict = stdClass()
    dicdir = os.path.join(core.PATH.APP, "dic")
    dicfile = os.path.join(dicdir, "default.json")

    # global dic
    if os.path.isfile(dicfile):
        try:
            filenames = os.listdir(dicdir)
            for filename in filenames:
                langname, ext = os.path.splitext(filename)
                if ext != ".json":
                    continue
                dicfile = os.path.join(dicdir, filename)
                if "__global__" not in mydict:
                    mydict.__global__ = dicObjClass()
                with open(dicfile) as data:
                    data = json.load(data)
                    data = stdClass(data)
                    mydict.__global__[langname.upper()] = data
        except: 
            pass

    # module dic
    for root, _, _ in os.walk(core.PATH.MODULES):
        dicdir = os.path.join(root, "dic")
        dicfile = os.path.join(dicdir, "default.json")

        if os.path.isfile(dicfile) == False:
            continue
        
        root = root.replace(core.PATH.MODULES + "/", "")
        ns = root.split('/')
        try:
            filenames = os.listdir(dicdir)
            for filename in filenames:
                langname, ext = os.path.splitext(filename)
                if ext != ".json":
                    continue
                dicfile = os.path.join(dicdir, filename)
                with open(dicfile) as data:
                    data = json.load(data)
                    data = stdClass(data)
                    tmp = mydict
                    for i in range(len(ns)):
                        n = ns[i]
                        if n not in tmp:
                            tmp[n] = dicObjClass()
                        if i == len(ns) - 1:    
                            tmp[n][langname.upper()] = data
                        tmp = tmp[n]
        except: 
            pass

    return mydict

class dicClass(dict):
    def __init__(self, root, obj=None, lang="DEFAULT", default_dic=None, default_dic_loc=[]):
        super(dicClass, self).__init__()
        self.obj = obj
        self.root = root
        self.lang = lang.upper()
        self.default_dic = default_dic
        self.default_dic_loc = default_dic_loc

    def set_language(self, lang):
        self.lang = lang.upper()

    def __getitem__(self, key):
        return self.__getattr__(key)

    def __getattr__(self, attr):
        try:
            self.default_dic_loc.append(attr)

            # if attr in obj
            if attr in self.obj:
                obj = self.obj[attr]

                # if instance is dicObjClass, find language class
                if isinstance(obj, dicObjClass):
                    if "DEFAULT" in obj: 
                        self.default_dic = obj["DEFAULT"]
                        self.default_dic_loc = []
                    langobj = None
                    if self.lang in obj:
                        langobj = obj[self.lang]
                    elif "DEFAULT" in obj:
                        langobj = obj["DEFAULT"]
                    if langobj is not None:
                        return dicClass(self.root, langobj, self.lang, self.default_dic, self.default_dic_loc)
                
                if obj is not None:
                    return dicClass(self.root, obj, self.lang, self.default_dic, self.default_dic_loc)
            
            locs = self.default_dic_loc
            if self.default_dic is not None:
                langobj = self.default_dic
                for attr in locs:
                    if attr in langobj:
                        langobj = langobj[attr]
                    else:
                        langobj = None
                        break
                if langobj is not None:
                    return dicClass(self.root, langobj, self.lang, self.default_dic, self.default_dic_loc)

            #  if not in obj, return global dic
            if '__global__' in self.root:
                if self.lang in self.root.__global__:
                    obj = self.root.__global__[self.lang]
                    if attr in obj:
                        return dicClass(self.root, obj[attr], self.lang, self.default_dic, self.default_dic_loc)
                    
                if "DEFAULT" in self.root.__global__:
                    obj = self.root.__global__["DEFAULT"]
                    if attr in obj:
                        return dicClass(self.root, obj[attr], self.lang, self.default_dic, self.default_dic_loc)
        except:
            pass

        return dicClass(self.root, None, self.lang, self.default_dic, self.default_dic_loc)

    def __str__ (self):
        obj = self.obj
        if isinstance(obj, dicObjClass):
            if self.lang in obj:
                return str(obj[self.lang])
            if "DEFAULT" in obj:
                return str(obj["DEFAULT"])
            return "{}"
        return str(obj)

if os.path.isdir(core.PATH.WEBSRC):
    framework = stdClass()
    framework.core = core
    framework.interfaces = interfaces
    framework.config = config
    __DIC__ = __finddic__()
    framework.dic = dicClass(__DIC__, __DIC__)
    framework.cache = cache
    
    bootstrap = bootstrap(framework).bootstrap