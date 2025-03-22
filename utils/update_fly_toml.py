import subprocess

import toml


def get_version():
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)
    return pyproject["project"]["version"]


def get_git_sha():
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def update_fly_toml(full_version):
    with open("fly.toml", "r") as f:
        fly_config = toml.load(f)

    fly_config["env"]["VERSION"] = full_version

    with open("fly.toml", "w") as f:
        toml.dump(fly_config, f)


version = get_version()
git_sha = get_git_sha()
full_version = f"{version}-{git_sha}"
update_fly_toml(full_version)
print(f"Updated fly.toml with version: {full_version}")
