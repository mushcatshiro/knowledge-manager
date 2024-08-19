import subprocess


def pytest_configure(config):
    from blog.utils import set_env_var

    set_env_var(".env.test")
    print("setting up docker containers")

    o = subprocess.run(
        [
            "cd",
            "..",
            "&&",
            "docker-compose",
            "-f",
            "docker-compose-test.yaml",
            "up",
            "-d",
        ],
        shell=True,
        capture_output=True,
    )
    print(o)


def pytest_unconfigure(config):
    """
    called before test process is exited.
    """
    o = subprocess.run(
        ["cd", "..", "&&", "docker-compose", "-f", "docker-compose-test.yaml", "down"],
        shell=True,
    )
    print(o)
