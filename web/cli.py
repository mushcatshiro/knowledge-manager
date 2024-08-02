import click

from blog.utils.envvars import set_env_var


"""
TODO
implement `migrate` and `revision` commands for alembic
test
"""


@click.command()
@click.option("--env", default=".env", help="Name of the environment file.")
def test(env: str) -> None:
    """Initialize the environment variables."""
    set_env_var(env)

    import pytest
    import sys

    print("Running tests...")
    sys.exit(pytest.main(["-qq"]))


@click.command()
@click.option("--env", default=".env", help="Name of the environment file.")
@click.option(
    "--alembic-cfg",
    default="alembic.ini",
    help="Name of the alembic configuration file.",
)
def deploy(env: str, alembic_cfg) -> None:
    """Initialize the environment variables."""
    set_env_var(env)

    from alembic import command
    from alembic.config import Config

    config = Config(alembic_cfg)
    command.upgrade(config, "head")


if __name__ == "__main__":
    test()
    # deploy()
