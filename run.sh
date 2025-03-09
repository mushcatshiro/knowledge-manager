#!/bin/sh

arg=$1

echo "Running the app"
. .venv/bin/activate
cd web/

mkdir /app/blogfiles

# if arg is plain then skip the below steps
if [ "$arg" != "plain" ]; then
    echo "Running the app with nginx"
    cp /app/conf/web /etc/nginx/sites-enabled/

    sed -i "s/include \/etc\/nginx\/sites-enabled\/\*;/include \/etc\/nginx\/sites-enabled\/\web;/" /etc/nginx/nginx.conf

    nginx -c /etc/nginx/nginx.conf

    nginx -s reload
fi

alembic upgrade head

# exec gunicorn -b :5000 --access-logfile - --error-logfile - app:app
export FLASK_APP=app.py
if [ "$arg" = "plain" ]; then
    echo "Running the app without nginx"
    flask run --host "0.0.0.0" -p 5000
else
    flask run -p 5000
fi
