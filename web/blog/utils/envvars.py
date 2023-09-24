import os


def set_env_var(fname=".env") -> None:
    if not os.path.exists(fname):
        raise FileNotFoundError
    with open(fname, "r", encoding="utf-8") as rf:
        config = rf.readlines()

    for pair in config:
        k, v = pair.split("=", 1)
        if v is not None and v != "":
            os.environ[k.upper()] = v
