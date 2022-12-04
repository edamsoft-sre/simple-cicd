#!/usr/bin/env python3.11

import tempfile
import typer
import subprocess
from subprocess import STDOUT, PIPE, CalledProcessError, TimeoutExpired
from pathlib import Path
from typing import Optional


def replace_key(filename: str, key: str, value: str) -> None:
    file = Path(filename)
    with open(file, 'r+') as f_in, tempfile.NamedTemporaryFile(
            'w', dir=Path(filename).parent, delete=False) as f_out:
        for line in f_in.readlines():
            if line.startswith(key):
                line = '='.join((line.split('=')[0], '"{}"\n'.format(value)))
            f_out.write(line)

        # remove old version
        Path.unlink(file)

        # rename new version
        temp = Path(f_out.name)
        temp.rename(filename)


def commit_changes() -> bool:
    try:
        commited = subprocess.run(["git", "commit", "-am"], stdout=PIPE, stderr=STDOUT, timeout=15)
    except CalledProcessError as error:
        print(error)
        return False


def main(image_tag: str,
         tfvars_file: Optional[str] = typer.Argument("deploy/deploy.auto.tfvars"),
         docker_repo: Optional[str] = typer.Argument("docker.io/edamsoft/turo")):
    key = "image_name"
    new_image = f"{docker_repo}:{image_tag}"
    replace_key(tfvars_file, key, new_image)


if __name__ == "__main__":
    typer.run(main)

