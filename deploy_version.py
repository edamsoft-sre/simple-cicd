#!/usr/bin/env python3.11
import os
import sys
import tempfile
import typer
import subprocess
import httpx
from subprocess import STDOUT, PIPE, CalledProcessError, TimeoutExpired
from pathlib import Path
from typing import Optional

TFVARS_FILE = "deploy/deploy.auto.tfvars"
DOCKER_REPO = "docker.io/edamsoft/turo"
ACCOUNT = "edam-software"
REPO = "turo"
TOKEN = os.getenv("GITHUB_TOKEN")
GITHUB_PULL = "https://api.github.com/repos/{}/{}/pulls"


def replace_key(filename: str, key: str, value: str) -> None:
    file = Path(filename)
    with open(file, 'r+') as f_in, tempfile.NamedTemporaryFile(
            'w', dir=Path(filename).parent, delete=False) as f_out:
        for line in f_in.readlines():
            if line.startswith(key):
                line = '='.join((line.split('=')[0], '"{}"\n'.format(value)))
            f_out.write(line)

        Path.unlink(file)
        temp = Path(f_out.name)
        temp.rename(filename)


def fetch_updates() -> bool:
    try:
        base = subprocess.run(["git", "checkout", "main"],
                              stdout=PIPE, stderr=STDOUT, timeout=15)
        fetch = subprocess.run(["git", "pull"],
                               stdout=PIPE, stderr=STDOUT, timeout=15)
        print(base.stdout.decode())
        print(fetch.stdout.decode())
    except CalledProcessError as error:
        print(error)
        return False
    return True


def create_branch(branch: str) -> bool:
    try:
        newbranch = subprocess.run(["git", "checkout", "-b", branch],
                                   stdout=PIPE, stderr=STDOUT, timeout=15)
        print(newbranch.stdout.decode())
    except CalledProcessError as error:
        print(error)
        return False
    return True


def commit_changes(image_tag: str) -> bool:
    try:
        commited = subprocess.run(["git", "commit", "-am", f"Updating new app image {image_tag}"],
                                  stdout=PIPE, stderr=STDOUT, timeout=15)
        print(commited.stdout.decode())
    except CalledProcessError as error:
        print(error)
        return False
    return True


def pull_request(account: str, repo: str, token: str, head: str,
                 base: Optional[str] = "main",
                 title: Optional[str] = None,
                 body: Optional[str] = None) -> bool:
    if title is None:
        commit = head.split("_")[1]
        title = f"Requesting approval to deploy image {commit}"
    if body is None:
        body = f"Please review deploy change in {head}"
    headers = {"Authorization": f"Bearer {token}", 'Accept': 'application/vnd.github+json'}
    data = {"title": title, "body": body, "head": head, "base": base}

    try:
        url = GITHUB_PULL.format(account, repo)
        resp = httpx.post(url, headers=headers, json=data)
    except httpx.HTTPStatusError as exc:
        print(exc)
        return False
    except httpx.RequestError as exc:
        print(exc)
        return False
    response = resp.json()
    try:
        print(response['url'])
    except KeyError as k:
        print(response['message'])
        return False
    return True


def push_changes(branch: str) -> bool:
    try:
        pushed = subprocess.run(["git", "push", "--set-upstream", "origin", branch],
                                stdout=PIPE, stderr=STDOUT, timeout=15)
    except CalledProcessError as error:
        print(error)
        return False
    return True


def run_tf_plan() -> bool:


def main(image_tag: str,
         tfvars_file: Optional[str] = typer.Argument(TFVARS_FILE),
         docker_repo: Optional[str] = typer.Argument(DOCKER_REPO),
         branch_prefix: Optional[str] = typer.Argument("deploy")):
    key = "image_name"
    new_image = f"{docker_repo}/{image_tag}"
    branch = f"{branch_prefix}_{image_tag}"
    fetch_updates() or sys.exit(1)
    create_branch(branch) or sys.exit(1)
    replace_key(tfvars_file, key, new_image)
    commit_changes(image_tag) or sys.exit(1)
    push_changes(branch) or sys.exit(1)
    plan = run_tf_plan()
    if plan:
        pull_request(ACCOUNT, REPO, TOKEN, branch, plan) or sys.exit(1)
    else:
        print("Error generating Terraform plan for PR")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
