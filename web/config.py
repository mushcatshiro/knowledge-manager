import logging
import os

from flask import request
from blog.utils.envvars import set_env_var

set_env_var()

basedir = os.path.abspath(os.path.dirname(__file__))


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request_ip = request.remote_addr
        return super().format(record)


class Config:
    PROJECTNAME = os.environ.get("PROJECTNAME")
    DSN = os.environ.get("DSN")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    BLOG_PATH = os.environ.get("BLOG_PATH")
    AUTH = os.environ.get("AUTH")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_PATH = os.environ.get("SESSION_COOKIE_PATH")
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = int(os.environ.get("PERMANENT_SESSION_LIFETIME"))
    SESSION_TYPE = os.environ.get("SESSION_TYPE")
    SESSION_FILE_THRESHOLD = int(os.environ.get("SESSION_FILE_THRESHOLD"))
    SITE_BASE_URL = os.environ.get("SITE_BASE_URL")

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        app.logger.handlers.clear()
        app.logger.setLevel(logging.DEBUG)
        formatter = RequestFormatter(
            "[%(asctime)s] %(levelname)s in %(module)s: %(message)s"
        )

        log_stream_handler = logging.StreamHandler()
        log_stream_handler.setFormatter(formatter)
        log_stream_handler.setLevel(logging.DEBUG)
        app.logger.addHandler(log_stream_handler)


class LocalDeploymentConfig(Config):
    pass


class CloudDeploymentConfig(Config):
    pass


config = {
    "default": TestingConfig,
    "production": LocalDeploymentConfig,
    "cloud": CloudDeploymentConfig,
}
