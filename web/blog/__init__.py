from flask import Flask
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy

from config import config


cors = CORS()
# db = SQLAlchemy()
ma = Marshmallow()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # TODO update CORS allowable resource    
    cors.init_app(app)
    # db.init_app(app)
    ma.init_app(app)

    from blog.app import main
    app.register_blueprint(main)
    # from blog.api import api
    # app.register_blueprint(api, url_prefix="/api")
    return app