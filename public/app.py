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
    segment = path.split('/')
    segment_idx = 0

    for ix in range(len(segment)):
        segment_idx = ix
        if ix == 0: 
            _segment = segment
        else: 
            _segment = segment[:-ix]

        _path = '/'.join(_segment)
        
        controller_path = os.path.join(PATH_PUBLIC, 'controller', module, _path , 'index.py')
        if os.path.isfile(controller_path):
            break
        
        controller_path = os.path.join(PATH_PUBLIC, 'controller', module, _path + '.py')
        if os.path.isfile(controller_path):
            break

    if os.path.isfile(controller_path) == False:
        segment_idx = len(segment)
        controller_path = os.path.join(PATH_PUBLIC, 'controller', module, 'index.py')
    
    if os.path.isfile(controller_path) == False:
        flask.abort(404)

    try:
        with open(controller_path, mode="r") as file:
            _tmp = {'Controller': None}
            ctrlcode = file.read()
            ctrlcode = 'import season\n' + ctrlcode
            exec(ctrlcode, _tmp)
            controller = _tmp['Controller']()
    except Exception as e:
        flask.abort(500)
        pass

    basepath = '/'.join(segment[:-segment_idx])
    segmentpath = '/'.join(segment[-segment_idx:])

    fnname = segmentpath.split('/')[0]
    if hasattr(controller, fnname):
        fnname = fnname
        segment_idx = segment_idx - 1
    elif hasattr(controller, '__index__'):
        fnname = '__index__'

    basepath = '/'.join(segment[:-segment_idx])
    segmentpath = '/'.join(segment[-segment_idx:])

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
            print(e)
            pass

    # process controller
    if hasattr(controller, '__startup__'):
        res = getattr(controller, '__startup__')(framework)
        if res is not None:
            return res

    if hasattr(controller, fnname):
        return getattr(controller, fnname)(framework)

    flask.abort(404)

# start web server
if __name__ == '__main__':
    app.run(host=loader("HOST", '0.0.0.0'), port=loader("PORT", 3002))
