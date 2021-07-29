import season
import flask

app = flask.Flask(__name__, static_url_path='')
season.bootstrap(app)

config = season.config.load()

host = config.get("host", "0.0.0.0")
port = int(config.get("port", 3000))

if __name__ == '__main__':
    app.run(host=host, port=port)