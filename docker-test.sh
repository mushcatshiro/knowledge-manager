source /app/.venv/bin/activate
cd web

python3 -m pytest --cov=app tests/
