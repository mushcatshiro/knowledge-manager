import os
import sys
from base64 import b64encode

sys.path.append(".")

import nacl.encoding
import requests
import click
from nacl import encoding, public
from blog.utils.envvars import set_env_var


def encrypt(public_key_for_repo: str, secret_value_input: str) -> str:
    sealed_box = public.SealedBox(
        public.PublicKey(public_key_for_repo.encode("utf-8"), encoding.Base64Encoder())
    )
    encrypted = sealed_box.encrypt(secret_value_input.encode("utf-8"))
    return b64encode(encrypted).decode("utf-8")


@click.command()
@click.option("--gha-env", default=".env.gha")
@click.option("--target-env")
@click.option("--secret-name")
def update_github_actions_secrets(gha_env, target_env, secret_name):
    if not os.path.exists(gha_env):
        raise ValueError("gha env file not found")
    if not os.path.exists(target_env):
        raise ValueError("target env file not found")
    set_env_var(gha_env)

    with open(target_env, "r", encoding="utf-8") as rf:
        config = rf.readlines()

    list_of_data = []
    # data = {}
    for pair in config:
        k, v = pair.split("=", 1)
        list_of_data.append(f'"{k.strip()}":"{v.strip()}"')
        # data[k.strip()] = v.strip()
    data = "{" + ",".join(list_of_data) + "}"
    # click.echo(data)

    with requests.Session() as session:
        # validate secret_name exists
        session.headers.update(
            {
                "Authorization": f"Bearer {os.getenv('PAT')}",
                "Accept": "application/vnd.github+json",
                "X-GitHub-Api-Version": "2022-11-28",
            }
        )
        resp = session.get(os.getenv("GHA_SECRET_LIST_URL"))
        resp = resp.json()
        # click.echo(resp)
        found = False
        for secret in resp["secrets"]:
            if secret["name"] == secret_name:
                click.echo(
                    f"secret created at: {secret['created_at']}, "
                    f"updated at: {secret['updated_at']}"
                )
                found = True
                break
        if not found:
            raise ValueError(f"Secret {secret_name} not found")
        # get public key
        resp = session.get(os.getenv("GH_GET_PUBLIC_KEY"))
        resp = resp.json()
        key_id = resp["key_id"]
        public_key = resp["key"]
        encrypted_value = encrypt(public_key, data)
        # update
        resp = session.put(
            os.getenv("GHA_SECRET_UPDATE_URL"),
            json={"encrypted_value": encrypted_value, "key_id": key_id},
        )
        print(resp.status_code)
        return
        if resp.status_code != 201 or resp.status_code != 204:
            raise ValueError(f"Failed to update secret wiht error message {resp.text}")
        # verify
        resp = session.get(os.getenv("GHA_SECRET_LIST_URL"))
        resp = resp.json()
        found = False
        for secret in resp["secrets"]:
            if secret["name"] == secret_name:
                click.echo(
                    f"secret created at: {secret['created_at']}, "
                    f"updated at: {secret['updated_at']}"
                )
        # trigger run?


if __name__ == "__main__":
    update_github_actions_secrets()
