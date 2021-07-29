# -*- coding: utf-8 -*-

import json
import os

class response:
    def __init__(self, framework):
        self.framework = framework
        self._flask = framework.flask
        self.data = response._data(framework)
        self.headers = self._headers()
        self.status_code = None
        self.mimetype = None
        self.modulename = framework.modulename

    def set_status(self, status_code):
        self.status_code = status_code

    def set_mimetype(self, mimetype):
        self.mimetype = mimetype

    def error(self, code=404, response="ERROR"):
        event = self.framework.core.CLASS.RESPONSE.STATUS(code=code, response=response)
        raise event
        
    # response functions
    def redirect(self, url):
        self.status_code = 302
        resp = self._flask.redirect(url)
        return self._build(resp)

    def download(self, filepath, as_attachment=True, filename=None):
        try:
            resp = self._flask.send_file(filepath, as_attachment=as_attachment, attachment_filename=filename)
            return self._build(resp)
        except:
            return self.error(404)
    
    def send(self, message, content_type=None):
        resp = self._flask.Response(str(message))
        if content_type is not None:
            self.headers.set('Content-Type', content_type)
        return self._build(resp)

    def json(self, obj):
        try:
            obj = dict(obj)
        except:
            pass
        obj = json.dumps(obj, default=self.framework.core.json_default)
        resp = self._flask.Response(str(obj))
        self.headers.set('Content-Type', 'application/json')
        return self._build(resp)

    def render(self, template_uri, module=None, **args):
        if module is None: module = self.modulename
        TEMPLATE_PATH = os.path.join(self.framework.core.PATH.PROJECT, 'public', 'templates', module, template_uri)
        TEMPLATE_URI = os.path.join(module, template_uri)
        self.data.set(**args)
        if os.path.isfile(TEMPLATE_PATH):
            data = self.data.get()
            resp = self._flask.render_template(TEMPLATE_URI, **data)
            return self._build(resp)

        self.error(404)

    # template varialbes
    class _data:
        def __init__(self, framework):
            self.framework = framework
            self.data = dict()
        
        def get(self, key=None):
            if key is None:
                return self.data
            if key in self.data:
                return self.data[key]
            return None

        def set(self, **args):
            for key, value in args.items():
                self.data[key] = value

        def set_json(self, **args):
            for key, value in args.items():
                self.data[key] = json.dumps(value, default=self.framework.core.json_default)

    # internal classes
    class _headers:
        def __init__(self):
            self.headers = {}
        
        def get(self):
            return self.headers

        def set(self, key, value):
            self.headers[key] = value

        def load(self, headers):
            self.headers = headers

        def flush(self):
            self.headers = {}

    # build response function
    def _build(self, response):
        headers = self.headers.get()
        for key in headers:
            response.headers[key] = headers[key]

        if self.status_code is not None:
            response.status_code = self.status_code
        else:
            response.status_code = 200

        if self.mimetype is not None:
            response.mimetype = self.mimetype

        event = self.framework.core.CLASS.RESPONSE.STATUS(code=response.status_code, response=response)
        raise event