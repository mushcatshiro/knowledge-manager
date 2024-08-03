import os

from blog import create_app
from blog.utils.envvars import set_env_var


if not os.getenv("DOCKER"):
    set_env_var()

app = create_app(os.environ.get("FLASK_MODE") or "default")
