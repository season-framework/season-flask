SKELETON_MODULE_CONTROLLER_INDEX = """import season

class Controller(season.interfaces.controller.base):

    # do action when controller started every time
    def __startup__(self, framework):
        # add default action (eg. acl)
        # return framework.response.redirect('/')
        pass

    # do action when segment is not defined
    def __default__(self, framework):
        response = framework.response
        message = framework.model('data').getMessage()
        response.data.set(title='Hello, World!', message=message)
        return response.render('default.pug')

    # do action when specific segment
    def mainpage(self, framework):
        response = framework.response
        response.data.set(title='Main Page', message=framework.request.segment.get(0, 'none'))
        return response.render('mainpage.pug')
"""

SKELETON_MODULE_VIEW_DEFAULT = """
h1= title
div {{ message }}
"""

SKELETON_MODULE_LIB_UTIL = """import string
import random

def randomstring(length=12):
    string_pool = string.ascii_letters + string.digits
    result = ""
    for i in range(length):
        result += random.choice(string_pool)
    return result
"""

SKELETON_MODULE_MODEL_DATA = """import season

class Model(season.interfaces.model.MySQL):
    def __init__(self, framework):
        super().__init__(framework)
        self.namespace = 'mysql' # database config namespace
        self.tablename = 'tablename' # tablename

    def getMessage(self):
        return self.framework.lib.util.randomstring()

    def single(self, id=None):
        sql = 'SELECT * FROM `{}` WHERE id=%s ORDER BY `id` DESC'.format(self.tablename)
        rows = self.query(sql, data=[id])
        if len(rows) == 0:
            return None
        return rows[0]

    def multi(self, page=1, dump=20):
        sql = 'SELECT * FROM `{}` LIMIT {}, {}'.format(self.tablename, (page - 1) * dump, dump)
        rows = self.query(sql)
        return rows
"""

SKELETON_FILTER = """import season

def ng(name):
    return '{{' + str(name) + '}}'

def process(framework):
    response = framework.response
    request = framework.request

    request_uri = request.uri()

    if request_uri == '/':
        return response.redirect("/dashboard")

    response.data.set(ng=ng)
"""

SKELETON_CONFIG = """from season import stdClass
config = stdClass()

config['filter'] = [
    'indexfilter'
]
"""

SKELETON_CONFIG_DATABASE = """from season import stdClass
config = stdClass()

config.mysql = stdClass()
config.mysql.host = '127.0.0.1'
config.mysql.user = 'dbuser'
config.mysql.password = 'dbpass'
config.mysql.database = 'databasename'
config.mysql.charset = 'utf8'
"""

SKELETON_INTERFACE_CONTROLLER = """import season

class base:    
    def __startup__(self, framework):
        self.__framework__ = framework
        
    def _status(self, status_code=200, data=dict()):
        res = season.stdClass()
        res.code = status_code
        res.data = data
        self.__framework__.response.set_status(status_code)
        return self.__framework__.response.json(res)
"""

SKELETON_INTERFACE_MODEL = """import season
import pymysql

def join(v, f='/'):
    if len(v) == 0:
        return ''
    return f.join(v)

class Empty:
    def __init__(self, framework):
        self.framework = framework

class MySQL:
    def __init__(self, framework):
        self.framework = framework
        self.config = framework.config.load('database')
        self.namespace = None
        self.tablename = None

    def query(self, sql, fetch=True, data=None):
        coninfo = None
        if self.namespace is not None:
            coninfo = self.config.data[self.namespace]
        else:
            coninfo = self.config.data.mysql
        
        con = pymysql.connect(**coninfo)
        if fetch:
            cur = con.cursor(pymysql.cursors.DictCursor)
        else:
            cur = con.cursor()
        rows = cur.execute(sql, data)
        if fetch:
            rows = cur.fetchall()
        else:
            con.commit()
        con.close()
        return rows

    def fields(self):
        tablename = self.tablename
        columns = self.query('DESC ' + tablename)

        result = season.stdClass()
        result.pk = []
        result.columns = []

        for col in columns:
            if col['Key'] == 'PRI':
                result.pk.append(col['Field'])
            result.columns.append(col['Field'])
        return result

    def get(self, **values):
        try:
            tablename = self.tablename
            fields = self.fields()

            w = []
            ps = []

            for key in values:
                if key not in fields.columns: continue
                w.append('`' + key + '`=%s')
                ps.append(str(values[key]))

            w = join(w, f=' AND ')

            sql = 'SELECT * FROM `' + tablename + '` WHERE ' + w
            res = self.query(sql, data=ps, fetch=True)

            if len(res) > 0:
                return res[0]

            return None
        except Exception as e:
            print(e)
            return None

    def rows(self, **values):
        try:
            tablename = self.tablename
            fields = self.fields()

            w = []
            ps = []

            orderby = None
            if 'orderby' in values:
                orderby = values['orderby']
                del values['orderby']

            limit = None
            if 'limit' in values:
                limit = values['limit']
                del values['limit']

            where = None
            if 'where' in values:
                where = values['where']
                del values['where']

            for key in values:
                if key not in fields.columns: continue
                w.append('`' + key + '`=%s')
                ps.append(str(values[key]))

            if len(w) > 0:
                w = join(w, f=' AND ')
                if where is not None: sql = 'SELECT * FROM `' + tablename + '` WHERE (' + where + ') AND ' + w
                else: sql = 'SELECT * FROM `' + tablename + '` WHERE ' + w
            elif where is not None:
                sql = 'SELECT * FROM `' + tablename + '` WHERE ' + where
            else:
                sql = 'SELECT * FROM `' + tablename + '`'
            
            if orderby is not None:
                sql = sql + ' ' + orderby
            if limit is not None:
                sql = sql + ' ' + limit

            res = self.query(sql, data=ps, fetch=True)            
            return res

        except Exception as e:
            return None

    def insert(self, values, **fn):
        try:
            tablename = self.tablename
            fields = self.fields()

            f = []
            v = []
            ps = []

            for key in values:
                if key not in fields.columns: continue
                f.append('`' + key + '`')
                if key in fn:
                    v.append('{}("{}")'.format(fn[key], str(values[key])))
                else:
                    v.append('%s')
                    ps.append(str(values[key]))

            f = join(f, f=',')
            v = join(v, f=',')

            sql = 'INSERT INTO `' + tablename + '`(' + f + ') VALUES(' + v + ')'
            res = self.query(sql, data=ps, fetch=False)

            if res == 0:
                return True, "Nothing Changed"

            return True, "Success"
        except Exception as e:
            return e

    def upsert(self, values, **fn):
        try:
            tablename = self.tablename
            fields = self.fields()

            f = []
            v = []
            s = []
            ps = []

            for key in values:
                if key not in fields.columns: continue
                f.append('`' + key + '`')
                if key in fn:
                    v.append('{}("{}")'.format(fn[key], str(values[key])))
                    s.append('`{}`={}("{}")'.format(key, fn[key], str(values[key])))
                else:
                    v.append('%s')
                    s.append('`' + key + '`=%s')
                    ps.append(str(values[key]))

            f = join(f, f=',')
            v = join(v, f=',')
            s = join(s, f=',')
            ps = ps + ps

            sql = 'INSERT INTO `' + tablename + '`(' + f + ') VALUES(' + v + ') ON DUPLICATE KEY UPDATE ' + s
            res = self.query(sql, data=ps, fetch=False)

            if res == 0:
                return True, "Nothing Changed"

            return True, "Success"
        except Exception as e:
            return e
"""