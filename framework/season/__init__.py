from _include import loader
import os
import shutil

from .framework import framework
from .core import stdClass

PATH_PROJECT = loader("PATH_PROJECT", "")

PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_FRAMEWORK = os.path.join(PATH_PROJECT, 'season-flask', 'framework')
PATH_MODULES = os.path.join(PATH_WEBSRC, 'modules')

PATH_TEMPLATE = os.path.join(PATH_PROJECT, 'season-flask', 'public', 'templates')
PATH_CONTROLLER = os.path.join(PATH_PROJECT, 'season-flask', 'public', 'controller')
PATH_APP = os.path.join(PATH_PROJECT, 'season-flask', 'public', 'websrc', 'app')

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
        targetpath = os.path.join(PATH_PROJECT, 'season-flask', 'public', 'templates', module)

        try:
            os.symlink(viewpath, targetpath)
        except:
            pass

    # build controller
    try:
        shutil.rmtree(PATH_CONTROLLER)
    except:
        pass

    try:
        os.makedirs(PATH_CONTROLLER, exist_ok=True)
    except:
        pass

    for module in os.listdir(PATH_MODULES):
        if module[0] == '.': continue
        ctrlpath = os.path.join(PATH_WEBSRC, 'modules', module, 'controller')
        if os.path.isdir(ctrlpath) == False:
            continue
        targetpath = os.path.join(PATH_PROJECT, 'season-flask', 'public', 'controller', module)

        try:
            os.symlink(ctrlpath, targetpath)
        except:
            pass

    # build websrc
    targetpath = os.path.join(PATH_PROJECT, 'season-flask', 'public', 'websrc')
    srcpath = os.path.join(PATH_WEBSRC)

    try:
        os.unlink(targetpath)
    except:
        pass

    if os.path.isdir(srcpath):
        try:
            os.symlink(srcpath, targetpath)
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

    # print(lv, keys[:lv], key, obj)
    return obj

interfaces_dir = os.path.join(PATH_FRAMEWORK, 'season', 'interfaces')
for dirpath, dirname, interfacenames in os.walk(interfaces_dir):
    if len(interfacenames) == 0: continue
    _dir = dirpath[len(interfaces_dir) + 1:]
    if len(_dir) == 0:
        _dir = []
    else:
        _dir = _dir.split('/')
    
    for interfacename in interfacenames:
        _class = os.path.join(dirpath, interfacename)
        try:
            with open(_class, mode="r") as file:
                _tmp = stdClass()
                _code = file.read()
                _code = 'import season\n' + _code
                exec(_code, _tmp)
                _build_interface(interfaces, _dir, interfacename, _tmp)
        except Exception as e:
            pass

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
        try:
            with open(_class, mode="r") as file:
                _tmp = stdClass()
                _code = file.read()
                _code = 'import season\n' + _code
                exec(_code, _tmp)
                _build_interface(interfaces, _dir, interfacename, _tmp)
        except Exception as e:
            pass
