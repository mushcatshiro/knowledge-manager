import os

import click

from utils import set_env_var
from utils.database import initialize_cloud, push
from search import *


@click.command()
@click.option("--fname", default=".env")
@click.option("--opt")
def main(fname, opt):
    set_env_var(fname)

    if opt == "initialize_cloud":
        initialize_cloud(os.environ.get("DSN"))
    elif opt == "push":
        push(os.environ.get("ABSDIR"), os.environ.get("DSN"))
    elif opt == "test":
        pass
    # elif opt == "query":
    #     ret = query(
    #         os.environ.get("DSN")
    #     )
    #     click.echo(ret)
    else:
        click.echo(f"opt: {opt} does not exists")


if __name__ == "__main__":
    main()
