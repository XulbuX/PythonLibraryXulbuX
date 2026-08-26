import ast
import os
import subprocess
import tomllib
from pathlib import Path
import pytest
import regex as rx

# Define paths relative to this test file `tests/test_metadata_consistency.py`:
ROOT_DIR = Path(__file__).parent.parent
PYPROJECT_PATH = ROOT_DIR / "pyproject.toml"
INIT_PATH = ROOT_DIR / "src" / "xulbux" / "__init__.py"


def get_current_branch() -> str | None:
    """Returns the current git branch name, or `None` if it cannot be determined."""

    # Check `GitHub` Actions environment variables first:
    if branch := os.environ.get("GITHUB_HEAD_REF") or os.environ.get("GITHUB_REF_NAME"):
        return branch

    # Fallback to Git command for local dev:
    try:
        result = subprocess.run(
            ["git", "branch", "--show-current"],
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


# ************************************************* VERSION CONSISTENCY TEST **************************************************


def test_version_consistency() -> None:
    """Verifies that the version numbers in `pyproject.toml` and `__init__.py`<br>
    match the version specified in the current release branch name (`dev/X.Y.Z`)."""

    # Skip if we can't determine the branch (detached head or not a git repo):
    if not (branch_name := get_current_branch()):
        pytest.skip("Could not determine git branch name")

    # Skip if branch name doesn't match release pattern `dev/X.Y.Z`:
    if not (branch_match := rx.match(r"^dev/([0-9]+\.[0-9]+\.[0-9]+)$", branch_name)):
        pytest.skip(f"Current branch '{branch_name}' is not a release branch (dev/X.Y.Z)")

    expected_version = branch_match.group(1)

    # Extract version from `__init__.py`:
    with open(INIT_PATH, encoding="utf-8") as file:
        init_content = file.read()
        init_version_match = rx.search(r'^__version__(?:[^=]*)?=\s*"([^"]+)"', init_content, rx.MULTILINE)
    init_version = init_version_match.group(1) if init_version_match else None

    # Extract version from `pyproject.toml`:
    with open(PYPROJECT_PATH, "rb") as file:
        pyproject_data = tomllib.load(file)
    pyproject_version = pyproject_data.get("project", {}).get("version", "")

    assert init_version is not None, f"Could not find var '__version__' in {INIT_PATH}"
    assert pyproject_version, f"Could not find var 'version' in {PYPROJECT_PATH}"

    assert init_version == expected_version, (
        f"Hardcoded lib-version in src/xulbux/__init__.py ({init_version}) does not match branch version ({expected_version})"
    )

    assert pyproject_version == expected_version, (
        f"Hardcoded lib-version in pyproject.toml ({pyproject_version}) does not match branch version ({expected_version})"
    )


# *********************************************** DEPENDENCIES CONSISTENCY TEST ***********************************************


def test_dependencies_consistency() -> None:
    """Verifies that dependencies in `pyproject.toml` match `__dependencies__` in `__init__.py`."""

    # Extract dependencies from `__init__.py`:
    with open(INIT_PATH, encoding="utf-8") as file:
        init_content = file.read()
    init_deps_match = rx.search(r"__dependencies__(?:[^=]*)?=\s*(\[.*?\])", init_content, rx.DOTALL)

    # Extract dependencies from `pyproject.toml`:
    with open(PYPROJECT_PATH, "rb") as file:
        pyproject_data = tomllib.load(file)
    pyproject_deps = pyproject_data.get("project", {}).get("dependencies", [])

    assert init_deps_match is not None, f"Could not find var '__dependencies__' in {INIT_PATH}"
    assert pyproject_deps, f"Could not find 'dependencies' in {PYPROJECT_PATH}"

    init_deps = ast.literal_eval(init_deps_match.group(1))

    # Sort for comparison:
    pyproject_deps_sorted = sorted(pyproject_deps)
    init_deps_sorted = sorted(init_deps)

    assert init_deps_sorted == pyproject_deps_sorted, (
        f"\nDependencies mismatch:\n  __init__.py    : {init_deps_sorted}\n  pyproject.toml : {pyproject_deps_sorted}\n"
    )


# *********************************************** DESCRIPTION CONSISTENCY TEST ************************************************


def test_description_consistency() -> None:
    """Verifies that the description in `pyproject.toml` matches `__description__` in `__init__.py`."""

    # Extract description from `__init__.py`:
    with open(INIT_PATH, encoding="utf-8") as file:
        init_content = file.read()
        init_desc_match = rx.search(r'^__description__(?:[^=]*)?=\s*"([^"]+)"', init_content, rx.MULTILINE)
    init_desc = init_desc_match.group(1) if init_desc_match else None

    # Extract description from `pyproject.toml`:
    with open(PYPROJECT_PATH, "rb") as file:
        pyproject_data = tomllib.load(file)
    pyproject_desc = pyproject_data.get("project", {}).get("description", "")

    assert init_desc is not None, f"Could not find var '__description__' in {INIT_PATH}"
    assert pyproject_desc, f"Could not find 'description' in {PYPROJECT_PATH}"

    assert init_desc == pyproject_desc, (
        f"\nDescription mismatch:\n  __init__.py    : {init_desc}\n  pyproject.toml : {pyproject_desc}\n"
    )
