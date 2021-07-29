import re

class request:
    def __init__(self, framework):
        self._flask = framework.flask
        self.framework = framework
        
    def method(self):
        return self._flask.request.method
        
    def client_ip(self):
        return self._flask.request.environ.get('HTTP_X_REAL_IP', self._flask.request.remote_addr)

    def language(self):
        headers = dict(self._flask.request.headers)
        lang = None
        if 'Framework-Language' in headers:
            lang = headers['Framework-Language']
        elif 'Accept-Language' in headers:
            lang = headers['Accept-Language']
            lang = lang[:2]
        return lang

    def uri(self):
        return self.request().path

    def match(self, pattern):
        uri = self.uri()
        x = re.search(pattern, uri)
        if x: return True
        return False

    def query(self, key=None, default=None):
        request = self.request()
        formdata = dict(request.values)

        if key is None:
            return formdata

        if key in formdata:
            return formdata[key]
        
        if default is True:
            self._flask.abort(400)
            
        return default

    def headers(self, key, default=None):
        headers = dict(self._flask.request.headers)
        if key in headers:
            return headers[key]
        return default

    def file(self):
        try:
            return self._flask.request.files['file']
        except:
            return None

    def files(self):
        try:
            return self._flask.request.files.getlist('file[]')
        except:
            return []

    def request(self):
        return self._flask.request
