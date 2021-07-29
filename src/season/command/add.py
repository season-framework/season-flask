import os
from argh import arg, expects_obj

PATH_FRAMEWORK = os.path.dirname(os.path.dirname(__file__))
PATH_PROJECT = os.path.join(os.getcwd())
PATH_PUBLIC = os.path.join(PATH_PROJECT, 'public')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')

@arg('component', default=None, help='module | filter | model')
@arg('namespace', default=None, help='name')
@arg('--uri', help='https://github.com/season-framework/module-name')
def add(component, namespace, uri=None):
    if os.path.isdir(PATH_PUBLIC) == False or os.path.isdir(PATH_WEBSRC) == False:
        print("Invalid Project path: season framework structure not found in this folder.")
        return
    
