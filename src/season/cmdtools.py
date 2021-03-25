import json
import re
import os

import argh
from argh import arg

@arg('projectname', default='sample-project', help='project name')
def create(projectname):
    basepath = os.path.join(os.getcwd(), projectname)
    if os.path.isdir(basepath):
        print("Already exists project path '{}'".format(basepath))
        return

    os.makedirs(basepath)
    print(basepath)

parser = argh.ArghParser()
parser.add_commands([
    create
])

def main():
    parser.dispatch()

if __name__ == '__main__':
    main()