#!/bin/sh
echo "Running the app"
. .venv/bin/activate
cd web/

alembic upgrade head

# exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app
export FLASK_APP=app.py
flask run -p 5000 --host 0.0.0.0
