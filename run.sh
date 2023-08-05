#!/bin/sh
source /app/.venv/bin/activate
cd web/

exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app