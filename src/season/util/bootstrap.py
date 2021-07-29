import os
import traceback
import flask
from werkzeug.exceptions import HTTPException

class stdClass(dict):
    def __init__(self, *args, **kwargs):
        super(stdClass, self).__init__(*args, **kwargs)
        for arg in args:
            if isinstance(arg, dict):
                for k, v in arg.iteritems():
                    self[k] = v

        if kwargs:
            for k, v in kwargs.iteritems():
                self[k] = v

    def __getattr__(self, attr):
        return self.get(attr)

    def __setattr__(self, key, value):
        self.__setitem__(key, value)

    def __setitem__(self, key, value):
        super(stdClass, self).__setitem__(key, value)
        self.__dict__.update({key: value})

    def __delattr__(self, item):
        self.__delitem__(item)

    def __delitem__(self, key):
        super(stdClass, self).__delitem__(key)
        del self.__dict__[key]

class bootstrap:
    def __init__(self, framework):
        self.response = None
        self.framework = framework

    def bootstrap(self, app):
        ERROR_INFO = stdClass()

        HTTP_METHODS = ['GET', 'HEAD', 'POST', 'PUT', 'DELETE', 'CONNECT', 'OPTIONS', 'TRACE', 'PATCH']
        framework = self.framework

        framework.core.build.template()

        # response handler
        @app.errorhandler(framework.core.CLASS.RESPONSE.STATUS)
        def handle_response(e):
            response, status_code = e.get_response()
            return response, status_code
            
        # Handler
        handler = stdClass()
        handler.onerror = framework.config.load().get('on_error', None)
        handler.before_request = framework.config.load().get('before_request', None)
        handler.after_request = framework.config.load().get('after_request', None)
        handler.build = framework.config.load().get('build', None)
        handler.build_resource = framework.config.load().get('build_resource', None)

        app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')
        if handler.build is not None:
            handler.build(app)

        # Exception Handler 
        @app.errorhandler(HTTPException)
        def handle_exception_http(e):
            print("[ERROR TRACEBACK URL] " + ERROR_INFO.path)
            if handler.onerror is not None:
                try:
                    framework.response.set_status(e.code)
                    return handler.onerror(framework, e.code, e)
                except Exception as ex:
                    if type(ex) == framework.core.CLASS.RESPONSE.STATUS:
                        return handle_response(ex)
                    raise ex
            return e.get_response()

        @app.errorhandler(Exception)
        def handle_exception(e):
            if type(e) == framework.core.CLASS.RESPONSE.STATUS: return handle_response(e)
            
            # TODO: error logging by option

            print("[ERROR TRACEBACK URL] " + ERROR_INFO.path)
            traceback.print_exc()
            if handler.onerror is not None:
                try:
                    framework.response.set_status(500)
                    return handler.onerror(framework, 500, e)
                except Exception as ex:
                    if type(ex) == framework.core.CLASS.RESPONSE.STATUS: return handle_response(ex)
            
            return '<!DOCTYPE HTML PUBLIC "-//W3C//DTD HTML 3.2 Final//EN"><title>500 Internal Server Error</title><h1>Internal Server Error</h1><p>The server encountered an internal error and was unable to complete your request. Either the server is overloaded or there is an error in the application.</p>', 500

        # Before Request
        @app.before_request
        def before_request():
            path = flask.request.path
            ERROR_INFO.path = path
            path = path.split("/")
            path = path[1:]
            if len(path) > 0:
                if path[0] == 'resources':
                    return

            # module finder
            def module_finder():
                for i in range(len(path)):
                    idx = len(path) - i
                    module = "/".join(path[:idx])
                    module_path = os.path.join(framework.core.PATH.MODULES, module)
                    uri_path = path[idx:]

                    for j in range(len(uri_path)):
                        uri_idx = len(uri_path) - j
                        controller_namespace = "/".join(uri_path[:uri_idx])
                        segment_path = "/".join(uri_path[uri_idx:])

                        controller_path = os.path.join(module_path, 'controller', controller_namespace, 'index.py')
                        if os.path.isfile(controller_path):
                            return module, module_path, controller_path, segment_path

                        controller_path = os.path.join(module_path, 'controller', controller_namespace + '.py')
                        if os.path.isfile(controller_path):
                            return module, module_path, controller_path, segment_path
                    
                    controller_path = os.path.join(module_path, 'controller', 'index.py')
                    if os.path.isfile(controller_path):
                        return module, module_path, controller_path, "/".join(uri_path)
                        
                return "", "", "", ""

            module, module_path, controller_path, segment_path = module_finder()

            ERROR_INFO.module = framework.modulename = module
            ERROR_INFO.modulepath = framework.modulepath = module_path
            ERROR_INFO.controllerpath = framework.controllerpath = controller_path
            ERROR_INFO.segmentpath = framework.segmentpath = segment_path

            framework._cache = stdClass()
            framework._cache.model = stdClass()
            framework.flask = flask

            framework.request = framework.core.CLASS.REQUEST(framework)
            framework.request.segment = framework.core.CLASS.SEGMENT(framework)
            framework.response = framework.core.CLASS.RESPONSE(framework)
            framework.lib = framework.core.CLASS.LIB(framework)
            
            framework.response.data.set(module=module)

            def model(modelname, module=None):
                if module is None: module = framework.modulename
                model_path = None
                if module is not None:
                    model_path = os.path.join(framework.core.PATH.MODULES, module, 'model', modelname + '.py')

                    if os.path.isfile(model_path) == False:
                        model_path = os.path.join(framework.core.PATH.APP, 'model', modelname + '.py')
                else:
                    model_path = os.path.join(framework.core.PATH.APP, 'model', modelname + '.py')

                if model_path in framework._cache.model:
                    return framework._cache.model[model_path]
                
                if os.path.isfile(model_path) == False:
                    framework.response.error(500, 'Model Not Found')

                with open(model_path, mode="rb") as file:
                    _tmp = {'Model': None}
                    _code = file.read().decode('utf-8')
                    exec(_code, _tmp)
                    framework._cache.model[model_path] = _tmp['Model'](framework)
                    return framework._cache.model[model_path]

            framework.model = model

            if handler.before_request is not None:
                handler.before_request(framework)

        @app.after_request
        def after_request(response):
            response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
            response.headers["Pragma"] = "no-cache"
            response.headers["Expires"] = "0"
            response.headers['Cache-Control'] = 'public, max-age=0'
            if handler.after_request is not None:
                res = handler.after_request(response)
                if res is not None: return res
            return response

        @app.route('/resources/<path:path>')
        def resources(path=''):
            path = path.split('/')
            
            # check module resource
            for i in range(len(path)):
                idx = len(path) - i
                module = "/".join(path[:idx])
                resource_filepath = "/".join(path[idx:])
                resource_dirpath = os.path.join(framework.core.PATH.WEBSRC, 'modules', module, 'resources')
                if os.path.isfile(os.path.join(resource_dirpath, resource_filepath)):
                    if handler.build_resource is not None:
                        res = handler.build_resource(resource_dirpath, resource_filepath)
                        if res is not None: return res
                    return flask.send_from_directory(resource_dirpath, resource_filepath)
            
            # global resource
            resource_abspath = os.path.join(framework.core.PATH.WEBSRC, 'resources', "/".join(path))
            if os.path.isfile(resource_abspath):
                resource_filepath = os.path.basename(resource_abspath)
                resource_dirpath = os.path.dirname(resource_abspath)
                if handler.build_resource is not None:
                    res = handler.build_resource(resource_dirpath, resource_filepath)
                    if res is not None: return res
                return flask.send_from_directory(resource_dirpath, resource_filepath)

            flask.abort(404)

        @app.route("/", methods=HTTP_METHODS)
        @app.route("/<string:module>", methods=HTTP_METHODS)
        @app.route("/<string:module>/", methods=HTTP_METHODS)
        @app.route("/<string:module>/<path:path>", methods=HTTP_METHODS)
        def catch_all(module='', path=''):
            path = f"{module}/{path}"
            path = path.split('/')
                
            module = framework.modulename
            controller_path = framework.controllerpath
            segment_path = framework.segmentpath

            # load config
            config = framework.config.load()

            # process filter
            filters = config.get('filter', [])
            for _filter in filters:
                filter_path = os.path.join(framework.core.PATH.WEBSRC, 'app', 'filter', _filter + '.py')
                if os.path.isfile(filter_path) == False:
                    continue
                    
                file = open(filter_path, mode="rb")
                _tmp = {'process': None}
                _code = file.read().decode('utf-8')
                file.close()
                exec(_code, _tmp)
                filter_fn = _tmp['process']
                res = filter_fn(framework)
                if res is not None:
                    return res
                
            # process controller
            if os.path.isfile(controller_path) == False:
                flask.abort(404)

            file = open(controller_path, mode="rb")
            _tmp = {'Controller': None}
            ctrlcode = file.read().decode('utf-8')
            file.close()
            exec(ctrlcode, _tmp)
            try:
                controller = _tmp['Controller'](framework)
            except:
                controller = _tmp['Controller']()
                
            fnname = segment_path.split('/')[0]
            if hasattr(controller, fnname):
                segment_path = segment_path[len(fnname)+1:]
                fnname = fnname
            elif hasattr(controller, '__default__'):
                fnname = '__default__'
            elif hasattr(controller, '__index__'):
                fnname = '__index__'
            else:
                flask.abort(404)

            framework.segmentpath = segment_path

            if controller is not None:
                controller.__framework__ = framework

                if hasattr(controller, '__startup__'):
                    res = getattr(controller, '__startup__')(framework)
                    if res is not None:
                        return res
                
                if hasattr(controller, fnname):
                    return getattr(controller, fnname)(framework)
                    


            flask.abort(404)
        