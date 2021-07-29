import time
import json
import sys
import os
import shutil
import zipfile
import datetime
import subprocess
import argh
import urllib.request
import psutil
import multiprocessing as mp
import subprocess

from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler

ROOT_PATH = os.path.dirname(os.path.realpath(__file__))
sys.path.insert(0, os.path.realpath(os.path.join(ROOT_PATH, '..')))
__package__ = "season"

from .version import VERSION_STRING

CACHE = {}

def run():
    def run_ctrl():
        publicpath = os.path.join(os.getcwd(), 'public')
        cmd = "cd {} && python app.py".format(publicpath)
        subprocess.call(cmd, shell=True)

    class Handler(FileSystemEventHandler):
        @staticmethod
        def on_any_event(event):
            CACHE['refresh'] = True
            CACHE['lasttime'] = time.time() * 1000

    mp.freeze_support()
    proc = mp.Process(target=run_ctrl)
    proc.start()

    event_handler = Handler()
    observer = Observer()
    observer.schedule(event_handler, os.path.join(os.getcwd(), 'websrc'), recursive=True)
    observer.start()

    try:
        CACHE['refresh'] = False
        CACHE['lasttime'] = time.time() * 1000

        while True:
            nd = datetime.datetime.now()
            now = time.time() * 1000
            diff = now - CACHE['lasttime']
            if CACHE['refresh'] and diff > 500:
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
                CACHE['refresh'] = False
                
            time.sleep(1)
    finally:
        observer.stop()
        observer.join()


def main():
    epilog = "Copyright 2021 proin <proin@season.co.kr>. Licensed under the terms of the MIT license. Please see LICENSE in the source code for more information."
    parser = argh.ArghParser()
    parser.add_commands([
        run
    ])
    parser.add_argument('--version', action='version', version='%(prog)s ' + VERSION_STRING)
    parser.dispatch()

if __name__ == '__main__':
    main()