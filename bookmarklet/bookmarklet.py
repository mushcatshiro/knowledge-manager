from flask import Flask, jsonify, request
from flask_cors import CORS
import click

import datetime as dt
import os
import sqlite3 as s


app = Flask(__name__)
cors = CORS(app, resources={r"/api/*": {"origins": "*"}})

BOOKMARKLET_STORAGE = "bookmarklet_storage"


@app.route("/api/bookmark", methods=["GET"])
def bookmark():
    payload = request.args.to_dict()
    now = dt.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
    conn = s.connect(os.environ.get(BOOKMARKLET_STORAGE))

    with conn:
        cur = conn.cursor()
        try:
            cur.execute(
                """
                INSERT INTO history (
                    page_title,
                    url,
                    desc,
                    img,
                    date,
                    is_pushed
                ) VALUES(?,?,?,?,?,?)
                """,
                (
                    payload["title"],
                    payload["url"],
                    payload["desc"],
                    payload["img"],
                    now,
                    0,
                ),
            )
        except s.IntegrityError:
            return jsonify({"status": "entry existed"}), 400
    return jsonify({"status": "success", "payload": payload})


@app.cli.command()
@click.option("--storage", required=True)
def init(storage):
    if not os.path.exists(storage):
        conn = s.connect(storage)
        with conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS history (
                    page_title TEXT NOT NULL,
                    url TEXT PRIMARY KEY NOT NULL,
                    desc TEXT,
                    img TEXT,
                    date TEXT NOT NULL,
                    is_pushed INT
                )
                """
            )


@app.cli.command()
@click.option("--storage", required=True)
def backup(storage, username, password, database, port):
    pass


@app.cli.command()
@click.option("--storage", required=True)
@click.option("--full", type=bool, default=False)
def inspect(storage, full):
    if os.path.exists(storage):
        conn = s.connect(storage)
        q = (
            "SELECT * FROM history"
            if full
            else "SELECT * FROM history WHERE is_pushed=0"
        )
        with conn:
            cur = conn.cursor()
            cur.execute(q)
            import json

            click.echo(json.dumps(cur.fetchall(), indent=2))


if __name__ == "__main__":
    import argparse

    parser = argparse.ArgumentParser()
    parser.add_argument("--storage", required=True)
    args = parser.parse_args()

    os.environ[BOOKMARKLET_STORAGE] = args.storage
    if not os.path.exists(args.storage):
        raise FileNotFoundError
    app.run(port=8080)
