from typing import Optional
from pathlib import Path
import subprocess
import pytest
import os
import re

# DEFINE PATHS RELATIVE TO THIS TEST FILE tests/test_version.py
ROOT_DIR = Path(__file__).parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"
INIT_PATH = ROOT_DIR / "src" / "xulbux" / "__init__.py"


def get_current_branch() -> Optional[str]:
    # CHECK GITHUB ACTIONS ENVIRONMENT VARIABLES FIRST
    # GITHUB_HEAD_REF IS SET FOR PULL REQUESTS (SOURCE BRANCH)
    if branch := os.environ.get("GITHUB_HEAD_REF"):
        return branch
    # GITHUB_REF_NAME IS SET FOR PUSHES (BRANCH NAME)
    if branch := os.environ.get("GITHUB_REF_NAME"):
        return branch

    # FALLBACK TO GIT COMMAND FOR LOCAL DEV
    try:
        result = subprocess.run(["git", "branch", "--show-current"], capture_output=True, text=True, check=True)
        return result.stdout.strip() or None
    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def get_file_version(file_path: Path, pattern: str) -> Optional[str]:
    if not file_path.exists():
        return None

    with open(file_path, "r", encoding="utf-8") as f:
        content = f.read()
        match = re.search(pattern, content, re.MULTILINE)
        if match:
            return match.group(1)

    return None


################################################## VERSION CONSISTENCY TEST ##################################################


def test_version_consistency():
    """Verifies that the version numbers in `pyproject.toml` and `__init__.py`
    match the version specified in the current release branch name (`dev/1.X.Y`)."""
    # SKIP IF WE CAN'T DETERMINE THE BRANCH (DETACHED HEAD OR NOT A GIT REPO)
    if not (branch_name := get_current_branch()):
        pytest.skip("Could not determine git branch name")

    # SKIP IF BRANCH NAME DOESN'T MATCH RELEASE PATTERN dev/1.X.Y
    if not (branch_match := re.match(r"^dev/(1\.[0-9]+\.[0-9]+)$", branch_name)):
        pytest.skip(f"Current branch '{branch_name}' is not a release branch (dev/1.X.Y)")

    expected_version = branch_match.group(1)

    # EXTRACT VERSIONS
    pyproject_version = get_file_version(PYPROJECT_PATH, r'^version\s*=\s*"([^"]+)"')
    init_version = get_file_version(INIT_PATH, r'^__version__\s*=\s*"([^"]+)"')

    assert pyproject_version is not None, f"Could not find var 'version' in {PYPROJECT_PATH}"
    assert init_version is not None, f"Could not find var '__version__' in {INIT_PATH}"

    assert pyproject_version == expected_version, \
        f"Hardcoded lib-version in pyproject.toml ({pyproject_version}) does not match branch version ({expected_version})"

    assert init_version == expected_version, \
        f"Hardcoded lib-version in src/xulbux/__init__.py ({init_version}) does not match branch version ({expected_version})"
