import time
import datetime
import traceback
import os

from flask import Flask, g, current_app, request, render_template
from flask.globals import request_ctx
from flask_cors import CORS
from flask_session import Session
from sqlalchemy import create_engine
from sqlalchemy.orm import declarative_base

from config import config


cors = CORS()
db = create_engine(os.environ.get("SQLALCHEMY_DATABASE_URI"))
sess = Session()

Base = declarative_base()


def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # TODO update CORS allowable resource
    cors.init_app(app)
    sess.init_app(app)

    from blog.app import main

    app.register_blueprint(main)

    from blog.auth import auth

    app.register_blueprint(auth, url_prefix="/auth")

    from blog.api import api

    app.register_blueprint(api, url_prefix="/api")

    from blog.admin import admin

    app.register_blueprint(admin, url_prefix="/admin")

    app.register_error_handler(Exception, error_handler)
    register_request_handlers(app, config_name)

    # TODO move this to config, fix multiple .env files (prod/test/devl) issue
    if os.environ.get("FLASK_MODE") == "testing":
        from sqlalchemy import create_engine

        from blog.utils import create_fake_data
        from blog.bookmark import BookmarkModel
        from blog.core.crud import CRUDBase

        test_db_engine = create_engine(
            os.environ.get("SQLALCHEMY_DATABASE_URI"), echo=True
        )
        # drop all tables
        Base.metadata.drop_all(test_db_engine)
        Base.metadata.create_all(test_db_engine)

        fake_data = create_fake_data(
            BookmarkModel, num=int(os.getenv("FAKE_DATA_NUM", 10))
        )
        basecrud = CRUDBase(BookmarkModel, test_db_engine)
        for data in fake_data:
            basecrud.safe_execute(operation="create", **data)

    return app


def register_request_handlers(app, config_name="default"):
    """
    TODO
    ----
    - profiler
    """

    @app.before_request
    def before_request_handler():
        g.request_received_time = time.time()
        g.context = {
            "unhandled": request.data if request.data else "",
            "form": dict(request.form) if request.form else {},
        }
        if request.content_type == "application/json":
            g.context["json"] = request.json

    @app.after_request
    def log_request(response):
        """
        TODO
        ----
        - exclude logic modification to prevent hard code
        """
        ctx = request_ctx
        if ctx.request.path in ["/favicon.ico"] or ctx.request.path.startswith(
            "/static"
        ):
            return response
        request_duration = time.time() - g.request_received_time
        data = {
            "user_agent": ctx.request.user_agent.string,
            "app_name": ctx.app.name,
            "date": str(datetime.date.today()),
            "request": f"{ctx.request.method} {ctx.request.url} {ctx.request.environ.get('SERVER_PROTOCOL')}",
            "url_args": {k: ctx.request.args[k] for k in ctx.request.args},
            "content_length": response.content_length,
            "blueprint": ctx.request.blueprint,
            "view_args": ctx.request.view_args,
            "path": ctx.request.path,
            "status_code": response.status_code,
            "remote_addr": ctx.request.remote_addr,
            "xforwardedfor": ctx.request.headers.get("X-Forwarded-For", None),
            "authorization": bool(ctx.request.authorization),
            "speed": float(request_duration),
            "payload": g.context,
        }
        current_app.logger.info(f"after request logging: {data}")
        return response

    if config_name == "debug":

        @app.after_request
        def profiler(response):
            return response


def error_handler(error):
    """
    TODO
    ----
    - to handle those with e.code and those without
    - return html or json based on request

    NOTE
    ----
    error handler runs before after_request
    """
    if not hasattr(error, "code"):
        error.code = 500
    if not hasattr(error, "description"):
        error.description = "Unexpected error raised within the code"
    if not hasattr(error, "name"):
        error.name = "Internal Server Error"
    current_app.logger.error({"error": error, "traceback": traceback.format_exc()})
    return (
        render_template(
            "error.html",
            error_code=error.code,
            error_msg=error.description,
            error_name=error.name,
        ),
        error.code,
    )


class CustomException(Exception):
    def __init__(self, code, description, name):
        self.code = code
        self.description = description
        self.name = name
        super().__init__(self, description)
