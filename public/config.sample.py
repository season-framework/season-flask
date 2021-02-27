# this is system config
import os
import lesscpy
from six import StringIO

# required
PATH_PROJECT = '<your-project-path>'
PORT = 3002

# optional
def build_app(app):
    app.secret_key = "test"
    
    # pip install pypugjs
    app.jinja_env.add_extension('pypugjs.ext.jinja.PyPugJSExtension')

resources_cache = dict()

def resource_handler(flask, resdir, path):
    fname, ext = os.path.splitext(path)
    filepath = os.path.join(resdir, path)

    if filepath in resources_cache:
        return resources_cache[filepath]

    if ext == '.less':
        f = open(filepath, 'r')
        lessfile = f.read()
        f.close()
        cssfile = lesscpy.compile(StringIO(lessfile), minify=True)
        response = flask.Response(str(cssfile))
        response.headers['Content-Type'] = 'text/css'
        resources_cache[filepath] = response
        return resources_cache[filepath]

    return None