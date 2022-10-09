import logging
import os


from flask import request


from utils import *


basedir = os.path.abspath(os.path.dirname(__file__))


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request_ip = request.remote_addr
        return super().format(record)


class Config:
    PROJECT_NAME = os.environ.get('PROJECT_NAME')

    @staticmethod
    def init_app(app):
        pass

class TestingConfig(Config):
    pass

class LocalDeploymentConfig(Config):
    pass

class CloudDeploymentConfig(Config):
    pass

config = {
    "default": TestingConfig,
    "production": LocalDeploymentConfig
}