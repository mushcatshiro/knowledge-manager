import os

from blog import create_app

app = create_app(os.environ.get("FLASK_MODE") or "default")
