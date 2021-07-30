import season
import flask

app = flask.Flask(__name__, static_url_path='')
if __name__ == '__main__':
    season.bootstrap(app)