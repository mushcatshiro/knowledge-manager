import logging
import os

from flask import request


basedir = os.path.abspath(os.path.dirname(__file__))


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request_ip = request.remote_addr
        return super().format(record)


class Config:
    PROJECT_NAME = os.environ.get("PROJECT_NAME")
    DSN = os.environ.get("DSN")
    SQLALCHEMY_DATABASE_URI = os.environ.get("SQLALCHEMY_DATABASE_URI")
    BLOG_PATH = os.environ.get("BLOG_PATH")
    AUTH = os.environ.get("AUTH")
    SECRET_KEY = os.environ.get("SECRET_KEY")
    SESSION_COOKIE_PATH = os.environ.get("SESSION_COOKIE_PATH")
    SESSION_COOKIE_SECURE = True
    PERMANENT_SESSION_LIFETIME = int(os.getenv("PERMANENT_SESSION_LIFETIME", 0))
    SESSION_TYPE = os.environ.get("SESSION_TYPE")
    SESSION_FILE_THRESHOLD = int(os.getenv("SESSION_FILE_THRESHOLD", 0))
    SITE_BASE_URL = os.environ.get("SITE_BASE_URL")
    PAGINATION_LIMIT = int(os.getenv("PAGINATION_LIMIT", 0))
    MAX_CONTENT_LENGTH = int(os.getenv("MAX_CONTENT_LENGTH", 0)) * 1000 * 1000
    ALLOWED_EXTENSIONS = os.getenv("ALLOWED_EXTENSIONS", "").split(",")
    IMAGE_URL_PREFIX = os.environ.get("IMAGE_URL_PREFIX")  # not directly used

    @staticmethod
    def init_app(app):
        pass


class TestingConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_NAME = os.environ.get("SQLALCHEMY_DATABASE_NAME")

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


class DeploymentConfig(Config):
    @classmethod
    def init_app(cls, app):
        Config.init_app(app)

        from logging import handlers

        app.logger.handlers.clear()
        app.logger.setLevel(logging.INFO)
        formatter = RequestFormatter(
            "[%(asctime)s] %(request_ip)s %(levelname)s in %(module)s: %(message)s",
        )

        logfile_handler = handlers.RotatingFileHandler(
            os.path.join(basedir, f"{cls.PROJECT_NAME}-PROD.log"),
            maxBytes=102400,
            backupCount=10,
            encoding="UTF-8",
        )
        logfile_handler.setFormatter(formatter)
        logfile_handler.setLevel(logging.INFO)
        app.logger.addHandler(logfile_handler)


class CloudDeploymentConfig(Config):
    pass


config = {
    "default": TestingConfig,
    "testing": TestingConfig,
    "production": DeploymentConfig,
    "cloud": CloudDeploymentConfig,
}
