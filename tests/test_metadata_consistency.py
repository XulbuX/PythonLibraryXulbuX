import ast
import os
import subprocess
import tomllib
from pathlib import Path
from typing import Any
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
            cwd=ROOT_DIR,
            stdin=subprocess.DEVNULL,
            capture_output=True,
            text=True,
            check=True,
        )
        return result.stdout.strip() or None

    except (subprocess.CalledProcessError, FileNotFoundError):
        return None


def _get_init_var(var_name: str) -> Any:
    """Extract a module-level variable value from `src/xulbux/__init__.py` using AST."""

    with open(INIT_PATH, encoding="utf-8") as file:
        tree = ast.parse(file.read(), filename=str(INIT_PATH))

    for node in tree.body:
        if isinstance(node, ast.AnnAssign) and isinstance(node.target, ast.Name) and node.target.id == var_name:
            if node.value is not None:
                return ast.literal_eval(node.value)

        elif isinstance(node, ast.Assign):
            for target in node.targets:
                if isinstance(target, ast.Name) and target.id == var_name:
                    return ast.literal_eval(node.value)

    return None


def _get_pyproject_data() -> dict[str, Any]:
    """Load and return the parsed `pyproject.toml` data dictionary."""

    with open(PYPROJECT_PATH, "rb") as file:
        return tomllib.load(file)


# ************************************************* VERSION CONSISTENCY TEST **************************************************


def test_version_consistency() -> None:
    """Verifies that the version numbers in `pyproject.toml` and `__init__.py`<br>
    match each other, and match the release branch (`dev/x.y.z`) if currently on one."""

    init_version = _get_init_var("__version__")
    pyproject_data = _get_pyproject_data()
    pyproject_version = pyproject_data.get("project", {}).get("version", "")

    assert init_version is not None, f"Could not find var '__version__' in {INIT_PATH}"
    assert pyproject_version, f"Could not find var 'version' in {PYPROJECT_PATH}"
    assert init_version == pyproject_version, (
        f"Version in __init__.py ({init_version}) does not match pyproject.toml ({pyproject_version})"
    )

    # If on a release branch, verify that the version matches the branch name:
    if (branch_name := get_current_branch()) and (branch_match := rx.match(r"^dev/([0-9]+\.[0-9]+\.[0-9]+)$", branch_name)):
        expected_version = branch_match.group(1)
        assert init_version == expected_version, (
            f"Hardcoded lib-version in src/xulbux/__init__.py ({init_version}) does not match branch ({expected_version})"
        )
        assert pyproject_version == expected_version, (
            f"Hardcoded lib-version in pyproject.toml ({pyproject_version}) does not match branch ({expected_version})"
        )


# *********************************************** DEPENDENCIES CONSISTENCY TEST ***********************************************


def test_dependencies_consistency() -> None:
    """Verifies that dependencies in `pyproject.toml` match `__dependencies__` in `__init__.py`."""

    init_deps = _get_init_var("__dependencies__")
    pyproject_data = _get_pyproject_data()
    pyproject_deps = pyproject_data.get("project", {}).get("dependencies", [])

    assert init_deps is not None, f"Could not find var '__dependencies__' in {INIT_PATH}"
    assert pyproject_deps, f"Could not find 'dependencies' in {PYPROJECT_PATH}"

    init_deps_sorted = sorted(init_deps)
    pyproject_deps_sorted = sorted(pyproject_deps)

    assert init_deps_sorted == pyproject_deps_sorted, (
        f"\nDependencies mismatch:\n  __init__.py    : {init_deps_sorted}\n  pyproject.toml : {pyproject_deps_sorted}\n"
    )


# *********************************************** DESCRIPTION CONSISTENCY TEST ************************************************


def test_description_consistency() -> None:
    """Verifies that the description in `pyproject.toml` matches `__description__` in `__init__.py`."""

    init_desc = _get_init_var("__description__")
    pyproject_data = _get_pyproject_data()
    pyproject_desc = pyproject_data.get("project", {}).get("description", "")

    assert init_desc is not None, f"Could not find var '__description__' in {INIT_PATH}"
    assert pyproject_desc, f"Could not find 'description' in {PYPROJECT_PATH}"

    assert init_desc == pyproject_desc, (
        f"\nDescription mismatch:\n  __init__.py    : {init_desc}\n  pyproject.toml : {pyproject_desc}\n"
    )


# ********************************************* REQUIRES PYTHON CONSISTENCY TEST **********************************************


def test_requires_python_consistency() -> None:
    """Verifies that `__requires_python__` in `__init__.py` matches `requires-python` in `pyproject.toml`."""

    init_req = _get_init_var("__requires_python__")
    pyproject_data = _get_pyproject_data()
    pyproject_req = pyproject_data.get("project", {}).get("requires-python", "")

    assert init_req is not None, f"Could not find var '__requires_python__' in {INIT_PATH}"
    assert pyproject_req, f"Could not find 'requires-python' in {PYPROJECT_PATH}"

    assert init_req == pyproject_req, (
        f"\nRequires-Python mismatch:\n  __init__.py    : {init_req}\n  pyproject.toml : {pyproject_req}\n"
    )


# ********************************************** AUTHOR & EMAIL CONSISTENCY TEST **********************************************


def test_author_and_email_consistency() -> None:
    """Verifies that `__author__` and `__email__` in `__init__.py` match `authors` in `pyproject.toml`."""

    init_author = _get_init_var("__author__")
    init_email = _get_init_var("__email__")
    pyproject_data = _get_pyproject_data()
    authors = pyproject_data.get("project", {}).get("authors", [])

    assert init_author is not None, f"Could not find var '__author__' in {INIT_PATH}"
    assert init_email is not None, f"Could not find var '__email__' in {INIT_PATH}"
    assert authors, f"Could not find 'authors' in {PYPROJECT_PATH}"

    first_author = authors[0]
    assert init_author == first_author.get("name"), (
        f"Author mismatch: __init__.py ({init_author}) vs pyproject.toml ({first_author.get('name')})"
    )
    assert init_email == first_author.get("email"), (
        f"Email mismatch: __init__.py ({init_email}) vs pyproject.toml ({first_author.get('email')})"
    )


# ************************************************* LICENSE CONSISTENCY TEST **************************************************


def test_license_consistency() -> None:
    """Verifies that `__license__` in `__init__.py` matches `license` in `pyproject.toml`."""

    init_license = _get_init_var("__license__")
    pyproject_data = _get_pyproject_data()
    pyproject_license = pyproject_data.get("project", {}).get("license", "")

    assert init_license is not None, f"Could not find var '__license__' in {INIT_PATH}"
    assert pyproject_license, f"Could not find 'license' in {PYPROJECT_PATH}"

    assert init_license == pyproject_license, (
        f"\nLicense mismatch:\n  __init__.py    : {init_license}\n  pyproject.toml : {pyproject_license}\n"
    )


# *************************************************** URL CONSISTENCY TEST ****************************************************


def test_url_consistency() -> None:
    """Verifies that `__url__` in `__init__.py` matches `Homepage` in `pyproject.toml`."""

    init_url = _get_init_var("__url__")
    pyproject_data = _get_pyproject_data()
    pyproject_url = pyproject_data.get("project", {}).get("urls", {}).get("Homepage", "")

    assert init_url is not None, f"Could not find var '__url__' in {INIT_PATH}"
    assert pyproject_url, f"Could not find 'Homepage' url in {PYPROJECT_PATH}"

    assert init_url == pyproject_url, f"\nURL mismatch:\n  __init__.py    : {init_url}\n  pyproject.toml : {pyproject_url}\n"


# *********************************************** PACKAGE NAME CONSISTENCY TEST ***********************************************


def test_package_name_consistency() -> None:
    """Verifies that `__package_name__` in `__init__.py` matches `name` in `pyproject.toml`."""

    init_name = _get_init_var("__package_name__")
    pyproject_data = _get_pyproject_data()
    pyproject_name = pyproject_data.get("project", {}).get("name", "")

    assert init_name is not None, f"Could not find var '__package_name__' in {INIT_PATH}"
    assert pyproject_name, f"Could not find 'name' in {PYPROJECT_PATH}"

    assert init_name == pyproject_name, (
        f"\nPackage name mismatch:\n  __init__.py    : {init_name}\n  pyproject.toml : {pyproject_name}\n"
    )
