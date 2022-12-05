#!/usr/bin/env python3.11
import os
import sys
import shutil
import tempfile
import typer
import subprocess
import httpx
from subprocess import STDOUT, PIPE, CalledProcessError, TimeoutExpired
from pathlib import Path
from typing import Optional

TMP_DIR = "/tmp/cicd_temp"
TF_PATH = "deploy"
TFVARS_FILE = f"{TF_PATH}/deploy.auto.tfvars"
KUBECONFIG_PATH = os.getenv("KUBE_CONFIG_PATH")
DOCKER_REPO = "docker.io/edamsoft/turo"
ACCOUNT = "edam-software"
REPO = "simple-cicd"
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


def clone_repo(account: str, repo: str, temp_dir: str = TMP_DIR) -> bool:
    directory = Path(temp_dir)
    if directory.exists():
        shutil.rmtree(temp_dir)
    os.mkdir(temp_dir)
    os.chdir(temp_dir)
    try:
        clone = subprocess.run(["git", "clone", f"https://github.com/{account}/{repo}.git"],
                               stdout=PIPE, stderr=STDOUT, timeout=15)
        print(clone.stdout.decode())
        os.chdir(repo)
    except CalledProcessError as error:
        print(error)
        return False
    return True


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


def pull_request(account: str, repo: str, token: str, head: str, plan: str,
                 base: Optional[str] = "main",
                 title: Optional[str] = None,
                 ) -> bool:
    commit = head.split("_")[1]
    if title is None:
        title = f"Requesting approval to deploy image {commit}"
    else:
        title = f"Requesting approval to deploy image {commit} - {title}"
    body = f"Please review terraform plan for branch {head}:\n {plan}"
    headers = {"Authorization": f"Bearer {token}", 'Accept': 'application/vnd.github+json'}
    data = {"title": title, "body": body, "head": head, "base": base, }

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
        print(f"Error creating pull request:\n{response['message']}")
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


def tf_init(tf_path: str) -> bool:
    try:
        os.chdir(tf_path)
        init = subprocess.run(["terraform", "init"],
                              stdout=PIPE, stderr=STDOUT, timeout=30)
    except CalledProcessError as error:
        print(error)
        return False
    output = init.stdout.decode()
    print(output)
    return True


def run_tf_plan(tf_path: str) -> str | None:
    try:
        plan = subprocess.run(["terraform", "plan", "-no-color", "-out", "tfplan"],
                              stdout=PIPE, stderr=STDOUT, timeout=30)
    except CalledProcessError as error:
        print(error)
        return None
    output = plan.stdout.decode()
    print(output)
    return output


def main(image_tag: str,
         title: Optional[str] = typer.Argument(''),
         tfvars_file: Optional[str] = typer.Argument(TFVARS_FILE),
         docker_repo: Optional[str] = typer.Argument(DOCKER_REPO),
         github_repo: Optional[str] = typer.Argument(REPO),
         github_account: Optional[str] = typer.Argument(ACCOUNT),
         branch_prefix: Optional[str] = typer.Argument("deploy")):
    key = "image_name"
    new_image = f"{docker_repo}:{image_tag}"
    branch = f"{branch_prefix}_{image_tag}"
    # clone_repo(github_account, github_repo) or sys.exit(1)
    fetch_updates() or sys.exit(1)
    create_branch(branch) or sys.exit(1)
    replace_key(tfvars_file, key, new_image)
    commit_changes(image_tag) or sys.exit(1)
    push_changes(branch) or sys.exit(1)
    tf_init(TF_PATH) or sys.exit(1)
    plan = run_tf_plan(TF_PATH)
    if 'Terraform will perform the following actions' in plan:
        pull_request(github_account, github_repo, TOKEN, branch, plan, title) or sys.exit(1)
    else:
        print("Error generating Terraform plan for PR")
        sys.exit(1)


if __name__ == "__main__":
    typer.run(main)
