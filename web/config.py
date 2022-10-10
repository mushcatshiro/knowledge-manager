import logging
import os

from flask import request

from utils import *
from utils.envvars import set_env_var

set_env_var()
basedir = os.path.abspath(os.path.dirname(__file__))


class RequestFormatter(logging.Formatter):
    def format(self, record):
        record.request_ip = request.remote_addr
        return super().format(record)


class Config:
    PROJECTNAME = os.environ.get('PROJECTNAME')
    DSN = os.environ.get("DSN")

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