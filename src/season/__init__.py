inapp = True
try:
    from _include import loader
except:
    inapp = False

if inapp:
    import os
    import shutil
    import datetime

    from .framework import framework
    from .core import stdClass
    from .version import VERSION_STRING
    __version__ = __VERSION__ = VERSION_STRING

    PATH_PROJECT = loader("PATH_PROJECT", "")

    PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
    PATH_FRAMEWORK = os.path.dirname(__file__)
    PATH_MODULES = os.path.join(PATH_WEBSRC, 'modules')

    PATH_TEMPLATE = os.path.join(PATH_PROJECT, 'public', 'templates')
    PATH_APP = os.path.join(PATH_PROJECT, 'websrc', 'app')

    def _bootstrap():
        # build templates
        try:
            shutil.rmtree(PATH_TEMPLATE)
        except:
            pass

        try:
            os.makedirs(PATH_TEMPLATE, exist_ok=True)
        except:
            pass

        for module in os.listdir(PATH_MODULES):
            if module[0] == '.': continue
            viewpath = os.path.join(PATH_WEBSRC, 'modules', module, 'view')
            if os.path.isdir(viewpath) == False:
                continue
            targetpath = os.path.join(PATH_PROJECT, 'public', 'templates', module)

            try:
                os.symlink(viewpath, targetpath)
            except:
                pass

    # add interfaces
    interfaces = stdClass()

    def _build_interface(obj, keys, instname, inst, lv=0):
        if len(keys) == 0 and obj is not None:
            bname = os.path.splitext(os.path.basename(instname))[0]
            obj[bname] = inst
            return obj

        if lv >= len(keys):
            bname = os.path.splitext(os.path.basename(instname))[0]
            _obj = stdClass()
            _obj[bname] = inst
            return _obj

        if obj is None: obj = stdClass()
        key = keys[lv]

        if key in obj:
            obj[key] = _build_interface(obj[key], keys, instname, inst, lv=lv+1)
        else: 
            obj[key] = _build_interface(None, keys, instname, inst, lv=lv+1)

        return obj

    interfaces_dir = os.path.join(PATH_FRAMEWORK, 'interfaces')
    for dirpath, dirname, interfacenames in os.walk(interfaces_dir):
        if len(interfacenames) == 0: continue
        _dir = dirpath[len(interfaces_dir) + 1:]
        if len(_dir) == 0:
            _dir = []
        else:
            _dir = _dir.split('/')
        
        for interfacename in interfacenames:
            _class = os.path.join(dirpath, interfacename)
            with open(_class, mode="r") as file:
                _tmp = stdClass()
                _code = file.read()
                exec(_code, _tmp)
                _build_interface(interfaces, _dir, interfacename, _tmp)

    interfaces_dir = os.path.join(PATH_APP, 'interfaces')
    for dirpath, dirname, interfacenames in os.walk(interfaces_dir):
        if len(interfacenames) == 0: continue
        _dir = dirpath[len(interfaces_dir) + 1:]
        if len(_dir) == 0:
            _dir = []
        else:
            _dir = _dir.split('/')
        
        for interfacename in interfacenames:
            _class = os.path.join(dirpath, interfacename)
            with open(_class, mode="r") as file:
                _tmp = stdClass()
                _code = file.read()
                exec(_code, _tmp)
                _build_interface(interfaces, _dir, interfacename, _tmp)

    def json_default(value): 
        if isinstance(value, datetime.date): 
            return value.strftime('%Y-%m-%d %H:%M:%S') 
        raise TypeError('not JSON serializable')