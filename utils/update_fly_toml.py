"""Utility script to update the version in fly.toml with the current git sha."""

import subprocess

import toml
import typer

app = typer.Typer()


def pick_up_cli_param_for_branch():
    """Pick up the CLI parameter for branch"""


def get_version():
    """Get the version from pyproject.toml"""
    with open("pyproject.toml", "r") as f:
        pyproject = toml.load(f)
    return pyproject["project"]["version"]


def get_git_sha():
    """Get the short git sha"""
    result = subprocess.run(
        ["git", "rev-parse", "--short", "HEAD"], stdout=subprocess.PIPE
    )
    return result.stdout.decode("utf-8").strip()


def get_git_branch() -> str:
    # Get the current branch name
    result = subprocess.run(
        ["git", "rev-parse", "--abbrev-ref", "HEAD"], stdout=subprocess.PIPE
    )
    branch_name = result.stdout.decode("utf-8").strip()
    return branch_name


def get_full_version() -> str:
    """Get the full version string"""
    branch_name = get_git_branch()
    version = get_version()
    git_sha = get_git_sha()
    # Check if the branch name is 'main'
    if branch_name == "main":
        # If so, set the version to the full version
        full_version = f"{version}-{git_sha}"
    else:
        # Otherwise, set the version to the branch name
        full_version = f"{version}-{git_sha}-{branch_name}"
    return full_version


@app.command()
def update_fly_toml():
    """Update the fly.toml with the new version"""
    full_version = get_full_version()

    try:
        # Load the fly.toml file
        with open("fly.toml", "r", encoding="utf-8") as f:
            fly_config = toml.load(f)

        fly_config["env"]["VERSION"] = full_version

        with open("fly.toml", "w") as f:
            toml.dump(fly_config, f)
        print(f"Updated fly.toml with version: {full_version}")
    except FileNotFoundError:
        print(
            "fly.toml file not found. Please make sure you are in the correct directory."
        )
    except toml.TomlDecodeError:
        print("Error decoding fly.toml file. Please check the file format.")
    except Exception as e:
        print(f"An error occurred: {e}")


if __name__ == "__main__":
    app()
