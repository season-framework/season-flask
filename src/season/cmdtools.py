import json
import re
import os
import shutil
import zipfile

import argh
from argh import arg

import urllib.request

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

    

parser = argh.ArghParser()
parser.add_commands([
    create
])

def main():
    parser.dispatch()

if __name__ == '__main__':
    main()