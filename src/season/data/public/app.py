import season
import flask

app = flask.Flask(__name__, static_url_path='')
isMain = __name__ == '__main__'
app = season.bootstrap(app, isMain)    
