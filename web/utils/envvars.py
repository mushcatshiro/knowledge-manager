import json
import os


def set_env_var(fname=".env") -> None:
    if not os.path.exists(fname):
        raise FileNotFoundError
    with open(fname, 'r') as rf:
        config = json.loads(rf.read())

    for k, v in config.items():
        if v is not None and v is not '':
            # allowing readable config files
            os.environ[k.replace('_', '').upper()] = v