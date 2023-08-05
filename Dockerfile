FROM python:3.7-alpine

WORKDIR /app

COPY poetry.lock pyproject.toml /app/

RUN apk update && apk add python3-dev gcc libc-dev libffi-dev

RUN pip install poetry && poetry config virtualenvs.in-project true && poetry install --with "production"

COPY web/ /app/web

COPY run.sh /app

ENTRYPOINT [ "./run.sh" ]