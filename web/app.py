import os

from blog import create_app
from blog.utils.envvars import set_env_var


set_env_var(".env.test")

app = create_app(os.environ.get("FLASK_MODE") or "default")
