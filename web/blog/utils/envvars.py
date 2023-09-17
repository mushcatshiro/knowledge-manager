import json
import os


def set_env_var(fname=".env") -> None:
    if not os.path.exists(fname):
        raise FileNotFoundError
    with open(fname, "r") as rf:
        try:
            config = json.loads(rf.read())
        except json.decoder.JSONDecodeError:
            config = json.loads(dict(rf.read()))

    for k, v in config.items():
        if v is not None and v is not "":
            # allowing readable config files
            # os.environ[k.replace('_', '').upper()] = v
            os.environ[k.upper()] = v
