#!/bin/sh
echo "Running the app"
. .venv/bin/activate
cd web/

mkdir /app/blogfiles

cp /app/conf/web /etc/nginx/sites-enabled/

sed -i "s/include \/etc\/nginx\/sites-enabled\/\*;/include \/etc\/nginx\/sites-enabled\/\web;/" /etc/nginx/nginx.conf

nginx -c /etc/nginx/nginx.conf

nginx -s reload

alembic upgrade head

# exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app
export FLASK_APP=app.py
flask run -p 5000
