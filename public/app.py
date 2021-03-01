# -*- coding: utf-8 -*-

import _include

import os
import sys
import json

import flask
import logging

from _include import loader

PATH_PROJECT = loader("PATH_PROJECT", "")
PATH_PUBLIC = os.path.join(PATH_PROJECT, 'season-flask', 'public')
PATH_FRAMEWORK = os.path.join(PATH_PROJECT, 'season-flask', 'framework')
PATH_WEBSRC = os.path.join(PATH_PROJECT, 'websrc')
PATH_MODULES = os.path.join(PATH_WEBSRC, 'modules')

sys.path.append(PATH_FRAMEWORK)
import season

season._bootstrap()

app = flask.Flask(__name__, static_url_path='')

build_app = loader("build_app")
if build_app is not None:
    build_app(app)

resource_handler = loader("resource_handler", None)

log = logging.getLogger('werkzeug')
log.disabled = True

HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']

@app.before_request
def filter():
    pass

@app.after_request
def add_header(response):
    response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
    response.headers["Pragma"] = "no-cache"
    response.headers["Expires"] = "0"
    response.headers['Cache-Control'] = 'public, max-age=0'
    return response

# resource handler
@app.route('/resources/<path:path>')
def resources(path=''):
    path = path.split('/')
    module = path[0]
    
    if len(path[1:]) > 0: path = "/".join(path[1:])
    else: path = ""

    # if file exists in module resources folder
    resdir = os.path.join(PATH_WEBSRC, 'modules', module, 'resources')
    if os.path.isfile(os.path.join(resdir, path)) == False:
        resdir = os.path.join(PATH_WEBSRC, 'resources')
        if len(path) == 0: path = module
        else: path = os.path.join(module, path)
        
    if os.path.isfile(os.path.join(resdir, path)) == False:
        flask.abort(404)
    
    if resource_handler is not None:
        res = resource_handler(flask, resdir, path)
        if res is not None:
            return res

    return flask.send_from_directory(resdir, path)

# module handler
@app.route("/", methods=HTTP_METHODS)
@app.route("/<string:module>", methods=HTTP_METHODS)
@app.route("/<string:module>/", methods=HTTP_METHODS)
@app.route("/<string:module>/<path:path>", methods=HTTP_METHODS)
def catch_all(module='', path=''):
    # load controller if exists
    module_path = os.path.join(PATH_WEBSRC, 'modules', module)
    segmentpath = ""

    if len(path) > 0: segment = path.split('/')
    else: segment = []

    basepath = ""
    segmentpath = ""
    controller_path = ""

    for ix in range(len(segment)):
        if ix == 0: 
            _segment = segment
        else: 
            _segment = segment[:-ix]

        _path = '/'.join(_segment)
        
        controller_path = os.path.join(PATH_PUBLIC, 'controller', module, _path , 'index.py')
        if os.path.isfile(controller_path):
            basepath = _path
            break
        
        controller_path = os.path.join(PATH_PUBLIC, 'controller', module, _path + '.py')
        if os.path.isfile(controller_path):
            basepath = _path
            break

    if os.path.isfile(controller_path) == False:
        basepath = ""
        controller_path = os.path.join(PATH_PUBLIC, 'controller', module, 'index.py')

    controller = None
    if len(basepath) > 0: segmentpath = path[len(basepath) + 1:]
    else: segmentpath = path

    if os.path.isfile(controller_path) == True:
        with open(controller_path, mode="r") as file:
            _tmp = {'Controller': None}
            ctrlcode = file.read()
            ctrlcode = 'import season\n' + ctrlcode
            exec(ctrlcode, _tmp)
            controller = _tmp['Controller']()

            fnname = segmentpath.split('/')[0]
            if hasattr(controller, fnname):
                segmentpath = segmentpath[len(fnname)+1:]
                fnname = fnname
            elif hasattr(controller, '__index__'):
                fnname = '__index__'
            else:
                flask.abort(404)

    # build framework object
    framework = season.framework.load(flask, module, segmentpath)
    
    config = framework.config.load()

    # process filter
    filters = config.get('filter', [])
    for _filter in filters:
        filter_path = os.path.join(PATH_PUBLIC, 'websrc', 'app', 'filter', _filter + '.py')

        if os.path.isfile(filter_path) == False:
            continue
            
        try:
            with open(filter_path, mode="r") as file:
                _tmp = {'process': None}
                _code = file.read()
                exec(_code, _tmp)
                filter_fn = _tmp['process']
                res = filter_fn(framework)
                if res is not None:
                    return res

        except Exception as e:
            raise e

    # process controller
    if controller is not None:
        controller.__framework__ = framework
        try:
            if hasattr(controller, '__startup__'):
                res = getattr(controller, '__startup__')(framework)
                if res is not None:
                    return res
        except Exception as e:
            # print('Error in ' + controller_path)
            raise e

        try:
            if hasattr(controller, fnname):
                return getattr(controller, fnname)(framework)
        except Exception as e:
            # print('Error in ' + controller_path)
            raise e

    flask.abort(404)

# start web server
if __name__ == '__main__':
    app.run(host=loader("HOST", '0.0.0.0'), port=loader("PORT", 3002))
