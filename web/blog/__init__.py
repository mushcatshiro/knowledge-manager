from flask import Flask, g, _request_ctx_stack, current_app, request, render_template
from flask_cors import CORS
from flask_marshmallow import Marshmallow
from flask_sqlalchemy import SQLAlchemy
import time
import datetime

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
        if request.method == "POST":
            g.context = request.json
        else:
            g.context = None

    @app.after_request
    def log_request(response):
        """
        TODO
        ----
        - exclude logic modification to prevent hard code
        """
        ctx = _request_ctx_stack.top
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
    """
    if not hasattr(e, "code"):
        e.code = 500
        e.description = "Unexpected error raised within the code"
        e.name = "Internal Server Error"
    return render_template(
        "error.html", error_code=e.code, error_msg=e.description, error_name=e.name
    ), 400