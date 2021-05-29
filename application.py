import flask
import json
from flask import request, Response

# Create and configure the Flask app
application = flask.Flask(__name__)
application.config.from_object('default_config')
application.debug = application.config['FLASK_DEBUG'] in ['true', 'True']


@application.route('/')
def index():
    return {"status":"ok","message":"DrinkKing API v1 at /api/v1/ in production mode"}


@application.route('/api/v1')
def shop():
    return "Hello"


if __name__ == '__main__':
    application.run(host='0.0.0.0')
