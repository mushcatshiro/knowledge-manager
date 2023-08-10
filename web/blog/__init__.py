from flask import Flask, g, current_app, request, render_template
from flask.globals import request_ctx
from flask_cors import CORS
from flask_marshmallow import Marshmallow
import time
import datetime
import traceback

from config import config


cors = CORS()
ma = Marshmallow()

def create_app(config_name):
    app = Flask(__name__)
    app.config.from_object(config[config_name])
    config[config_name].init_app(app)

    # TODO update CORS allowable resource    
    cors.init_app(app)
    ma.init_app(app)

    from blog.app import main
    app.register_blueprint(main)

    from blog.auth import auth
    app.register_blueprint(auth, url_prefix="/auth")

    from blog.api import api
    app.register_blueprint(api, url_prefix="/api")

    app.register_error_handler(Exception, error_handler)
    register_request_handlers(app, config_name)
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
        if ctx.request.path in ['/favicon.ico'] or ctx.request.path.startswith('/static'):
            return response
        request_duration = time.time() - g.request_received_time
        data = {
            'user_agent': ctx.request.user_agent.string,
            'app_name': ctx.app.name,
            'date': str(datetime.date.today()),
            'request': "{} {} {}".format(
                ctx.request.method,
                ctx.request.url,
                ctx.request.environ.get('SERVER_PROTOCOL')
            ),
            'url_args': dict(
                [(k, ctx.request.args[k]) for k in ctx.request.args]
            ),
            'content_length': response.content_length,
            'blueprint': ctx.request.blueprint,
            'view_args': ctx.request.view_args,
            'path': ctx.request.path,
            'status_code': response.status_code,
            'remote_addr': ctx.request.remote_addr,
            'xforwardedfor': ctx.request.headers.get('X-Forwarded-For', None),
            'authorization': bool(ctx.request.authorization),
            'speed': float(request_duration),
            'payload': g.context,
        }
        current_app.logger.info(f'after request logging: {data}')
        return response
    
    if config_name == "debug":
        @app.after_request
        def profiler(response):
            return response

def error_handler(e):
    """
    TODO
    ----
    - to handle those with e.code and those without
    - return html or json based on request

    NOTE
    ----
    error handler runs before after_request
    """
    if not hasattr(e, "code"):
        e.code = 500
        e.description = "Unexpected error raised within the code"
        e.name = "Internal Server Error"
    current_app.logger.error({"error": e, "traceback": traceback.format_exc()})
    return render_template(
        "error.html", error_code=e.code, error_msg=e.description, error_name=e.name
    ), 400