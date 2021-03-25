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
from argh import arg

import urllib.request
import psutil

from .version import VERSION_STRING

def download_url(url, save_path):
    with urllib.request.urlopen(url) as dl_file:
        with open(save_path, 'wb') as out_file:
            out_file.write(dl_file.read())

@arg('projectname', default='sample-project', help='project name')
def create(projectname):
    PROJECT_SRC = os.path.join(os.getcwd(), projectname)
    if os.path.isdir(PROJECT_SRC):
        shutil.rmtree(PROJECT_SRC)
        # print("Already exists project path '{}'".format(PROJECT_SRC))
        # return
    
    os.makedirs(PROJECT_SRC)

    # make websrc
    WEBSRC = os.path.join(PROJECT_SRC, 'websrc')
    os.makedirs(WEBSRC)

    # build web server
    PUBLIC_ZIP = os.path.join(PROJECT_SRC, 'public.zip')
    PUBLIC_SRC = os.path.join(PROJECT_SRC, 'public')
    
    download_url("https://github.com/season-framework/season-flask-public/archive/refs/heads/main.zip", PUBLIC_ZIP)
    zip_ref = zipfile.ZipFile(PUBLIC_ZIP, 'r')
    zip_ref.extractall(PROJECT_SRC)
    shutil.move(os.path.join(PROJECT_SRC, 'season-flask-public-main'), PUBLIC_SRC)
    os.remove(PUBLIC_ZIP)

    # shutil.copy(os.path.join(PUBLIC_SRC, 'config.sample.py'), os.path.join(PUBLIC_SRC, 'config.py'))

    f = open(os.path.join(PUBLIC_SRC, 'config.sample.py'), mode="r")
    config_sample = f.read()
    config_sample = config_sample.replace('<project-path>', PROJECT_SRC)
    f.close()

    f = open(os.path.join(PUBLIC_SRC, 'config.py'), mode="w")
    f.write(config_sample)
    f.close()

cache = {}

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

def main():
    epilog = "Copyright 2021 proin <proin@season.co.kr>. Licensed under the terms of the MIT license. Please see LICENSE in the source code for more information."
    parser = argh.ArghParser()
    parser.add_commands([
        create, run
    ])
    parser.add_argument('--version',
                    action='version',
                    version='%(prog)s ' + VERSION_STRING)
    parser.dispatch()

if __name__ == '__main__':
    main()