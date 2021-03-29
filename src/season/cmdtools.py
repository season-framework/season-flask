import time
import json
import re
import os
import shutil
import zipfile
import datetime

import subprocess
import multiprocessing as mp

import argh
from argh import arg, expects_obj

import urllib.request
import psutil
import subprocess

from .version import VERSION_STRING
from .skeleton import *

def write_file(path, content):
    f = open(path, mode="w")
    f.write(content)
    f.close()

def download_url(url, save_path):
    with urllib.request.urlopen(url) as dl_file:
        with open(save_path, 'wb') as out_file:
            out_file.write(dl_file.read())

def git(uri, path, dev):
    output = os.system('git clone {} {}'.format(uri, path))
    if os.path.isdir(os.path.join(path, '.git')) == False:
        raise Exception('Not git repo')

    if dev is None: shutil.rmtree(os.path.join(path, '.git'))

@arg('projectname', default='sample-project', help='project name')
def create(projectname):
    PROJECT_SRC = os.path.join(os.getcwd(), projectname)
    if os.path.isdir(PROJECT_SRC):
        print("Already exists project path '{}'".format(PROJECT_SRC))
        return
    
    os.makedirs(PROJECT_SRC)

    # build web server
    PUBLIC_ZIP = os.path.join(PROJECT_SRC, 'public.zip')
    PUBLIC_SRC = os.path.join(PROJECT_SRC, 'public')
    
    download_url("https://github.com/season-framework/season-flask-public/archive/refs/heads/main.zip", PUBLIC_ZIP)
    zip_ref = zipfile.ZipFile(PUBLIC_ZIP, 'r')
    zip_ref.extractall(PROJECT_SRC)
    shutil.move(os.path.join(PROJECT_SRC, 'season-flask-public-main'), PUBLIC_SRC)
    os.remove(PUBLIC_ZIP)

    # create public config
    f = open(os.path.join(PUBLIC_SRC, 'config.sample.py'), mode="r")
    config_sample = f.read()
    config_sample = config_sample.replace('<project-path>', PROJECT_SRC)
    f.close()

    f = open(os.path.join(PUBLIC_SRC, 'config.py'), mode="w")
    f.write(config_sample)
    f.close()

    # make websrc
    PATH_WEBSRC = os.path.join(PROJECT_SRC, 'websrc')
    os.makedirs(PATH_WEBSRC)

    # build default websrc
    PATH_RESOURCES = os.path.join(PATH_WEBSRC, 'resources')
    PATH_MODULE = os.path.join(PATH_WEBSRC, 'modules')
    PATH_APP = os.path.join(PATH_WEBSRC, 'app')
    PATH_FILTER = os.path.join(PATH_APP, 'filter')
    PATH_CONFIG = os.path.join(PATH_APP, 'config')
    PATH_INTERFACE = os.path.join(PATH_APP, 'interfaces')
    PATH_MODEL = os.path.join(PATH_APP, 'model')
    PATH_LIB = os.path.join(PATH_APP, 'lib')

    os.makedirs(PATH_RESOURCES)
    os.makedirs(PATH_MODULE)
    os.makedirs(PATH_APP)
    
    os.makedirs(PATH_CONFIG)
    write_file(os.path.join(PATH_CONFIG, 'config.py'), SKELETON_CONFIG)
    write_file(os.path.join(PATH_CONFIG, 'database.py'), SKELETON_CONFIG_DATABASE)

    os.makedirs(PATH_INTERFACE)
    write_file(os.path.join(PATH_INTERFACE, 'model.py'), SKELETON_INTERFACE_MODEL)
    write_file(os.path.join(PATH_INTERFACE, 'controller.py'), SKELETON_INTERFACE_CONTROLLER)
    
    os.makedirs(PATH_FILTER)
    write_file(os.path.join(PATH_FILTER, 'indexfilter.py'), SKELETON_FILTER)

    os.makedirs(PATH_LIB)
    write_file(os.path.join(PATH_LIB, 'util.py'), SKELETON_MODULE_LIB_UTIL)

    os.makedirs(PATH_MODEL)
    write_file(os.path.join(PATH_MODEL, 'data.py'), SKELETON_MODULE_MODEL_DATA)

cache = {}

# for run
def run_ctrl():
    publicpath = os.path.join(os.getcwd(), 'public')
    cmd = "cd {} && python app.py".format(publicpath)
    subprocess.call(cmd, shell=True)

def run():
    mp.freeze_support()
    
    from watchdog.observers import Observer
    from watchdog.events import FileSystemEventHandler

    proc = mp.Process(target=run_ctrl)
    proc.start()

    class Handler(FileSystemEventHandler):
        @staticmethod
        def on_any_event(event):
            cache['refresh'] = True
            cache['lasttime'] = time.time() * 1000

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, os.path.join(os.getcwd(), 'websrc'), recursive=True)
    observer.start()

    try:
        cache['refresh'] = False
        cache['lasttime'] = time.time() * 1000

        while True:
            nd = datetime.datetime.now()
            now = time.time() * 1000
            diff = now - cache['lasttime']
            if cache['refresh'] and diff > 500:
                print('\n\nrestarted at {}'.format(nd))
                try:
                    for child in psutil.Process(proc.pid).children(recursive=True):
                        child.kill()
                except Exception as e:
                    pass
                try:
                    proc = mp.Process(target=run_ctrl)
                    proc.start()
                except Exception as e:
                    pass
                cache['refresh'] = False
                
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()

@arg('component', default=None, help='module | filter | model')
@arg('namespace', default=None, help='name')
@arg('--uri', help='https://github.com/season-framework/module-name')
def add(component, namespace, uri=None):
    PATH_PUBIC = os.path.join(os.getcwd(), 'public')
    PATH_WEBSRC = os.path.join(os.getcwd(), 'websrc')
    PATH_MODULE = os.path.join(PATH_WEBSRC, 'modules')
    PATH_APP = os.path.join(PATH_WEBSRC, 'app')
    PATH_FILTER = os.path.join(PATH_APP, 'filter')
    PATH_MODEL = os.path.join(PATH_APP, 'model')
    
    if os.path.isdir(PATH_PUBIC) == False or os.path.isdir(PATH_WEBSRC) == False:
        print("Move to season-flask project root location")
        return
        
    if component == 'module':
        PATH_TARGET = os.path.join(PATH_MODULE, namespace)

        if os.path.isdir(PATH_TARGET):
            print("Module '{}' already exists".format(namespace))
            return

        repo = None
        dev = None
        PATH_CONFIG = os.path.join(os.getcwd(), 'sf.json')
        if os.path.isfile(PATH_CONFIG):
            f = open(PATH_CONFIG)
            config = json.load(f)
            f.close()
            if 'repo' in config:
                repo = config['repo']
            if 'dev' in config:
                dev = config['dev']

        if uri is not None:
            if '://' in uri:
                git(uri, PATH_TARGET, dev)
            elif repo is not None:
                uri = os.path.join(repo, uri)
                git(uri, PATH_TARGET, dev)
            else:
                print('module not found')
            return

        try:
            if repo is not None:
                uri = os.path.join(repo, namespace)
                git(uri, PATH_TARGET, dev) 
                return
        except:
            pass

        print('build default module template...')
        os.makedirs(PATH_TARGET)
        os.makedirs(os.path.join(PATH_TARGET, 'resources'))
        os.makedirs(os.path.join(PATH_TARGET, 'controller'))
        write_file(os.path.join(PATH_TARGET, 'controller', 'index.py'), SKELETON_MODULE_CONTROLLER_INDEX)

        os.makedirs(os.path.join(PATH_TARGET, 'model'))
        write_file(os.path.join(PATH_TARGET, 'model', 'data.py'), SKELETON_MODULE_MODEL_DATA)

        os.makedirs(os.path.join(PATH_TARGET, 'lib'))
        write_file(os.path.join(PATH_TARGET, 'lib', 'util.py'), SKELETON_MODULE_LIB_UTIL)

        os.makedirs(os.path.join(PATH_TARGET, 'view'))
        write_file(os.path.join(PATH_TARGET, 'view', 'default.pug'), SKELETON_MODULE_VIEW_DEFAULT)
        write_file(os.path.join(PATH_TARGET, 'view', 'mainpage.pug'), SKELETON_MODULE_VIEW_DEFAULT)

    if component == 'filter':
        PATH_TARGET = os.path.join(PATH_FILTER, namespace + '.py')

        if os.path.isfile(PATH_TARGET):
            print("Filter '{}' already exists".format(namespace))
            return

        write_file(PATH_TARGET, SKELETON_FILTER)

    if component == 'model':
        PATH_TARGET = os.path.join(PATH_MODEL, namespace + '.py')

        if os.path.isfile(PATH_TARGET):
            print("Model '{}' already exists".format(namespace))
            return

        write_file(PATH_TARGET, SKELETON_MODULE_MODEL_DATA)

@arg('--set', default=None, help='repo')
@arg('--unset', default=None, help='repo')
@arg('--value', default=None, help='https://git')
@expects_obj
def config(args):
    PATH_PUBIC = os.path.join(os.getcwd(), 'public')
    PATH_WEBSRC = os.path.join(os.getcwd(), 'websrc')
    if os.path.isdir(PATH_PUBIC) == False or os.path.isdir(PATH_WEBSRC) == False:
        print("Move to season-flask project root location")
        return

    PATH_CONFIG = os.path.join(os.getcwd(), 'sf.json')

    if os.path.isfile(PATH_CONFIG) == False:
        write_file(PATH_CONFIG, '{}')

    f = open(PATH_CONFIG)
    config = json.load(f)
    f.close()

    if args.set is not None:
        config[args.set] = args.value

    if args.unset is not None:
        del config[args.unset]

    write_file(PATH_CONFIG, json.dumps(config, sort_keys=True, indent=4))

def main():
    epilog = "Copyright 2021 proin <proin@season.co.kr>. Licensed under the terms of the MIT license. Please see LICENSE in the source code for more information."
    parser = argh.ArghParser()
    parser.add_commands([
        create, run, add, config
    ])
    parser.add_argument('--version',
                    action='version',
                    version='%(prog)s ' + VERSION_STRING)
    parser.dispatch()

if __name__ == '__main__':
    main()