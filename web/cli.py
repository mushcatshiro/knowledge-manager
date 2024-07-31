import click


from blog.utils.envvars import set_env_var


@click.command()
@click.option("--fname", default=".env", help="Name of the environment file.")
def init(fname: str) -> None:
    """Initialize the environment variables."""
    set_env_var(fname)


if __name__ == "__main__":
    init()
