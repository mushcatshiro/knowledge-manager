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

    click.echo("Running tests...")
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


@click.command()
@click.option("--mode", default="default")
@click.option("--output-name", default=".env")
def create_config(mode, output_name):
    cfg_template = "{name}={value}\n"
    cfg_out = ""
    from config import config

    cfg = config[mode]
    for key in dir(cfg):
        if key.isupper():
            val = click.prompt(f"Please enter value for {key}", type=str)
            cfg_out += cfg_template.format(name=key, value=val)
    with open(output_name, "w") as f:
        f.write(cfg_out)


if __name__ == "__main__":
    # test()
    # deploy()
    create_config()
