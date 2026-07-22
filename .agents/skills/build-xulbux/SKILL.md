---
name: build-xulbux
description: Compiles and builds the xulbux MyPyC library, and generates PYI stubs.
---

# build-xulbux

Use this skill to verify that the `xulbux` library fully compiles via MyPyC, generates the correct `.pyi` stub files, and packages/installs successfully.

## 1. Verify Stub Generation

Run the following command to only generate the `.pyi` stub files to the project root without clearing them. This allows you to inspect them and verify they are generated correctly.

**On Windows:**

CD into the project root, then run:

```powershell
py setup.py --create-stubs
```

**On Unix:**

CD into the project root, activate the `.venv` virtual environment, then run:

```bash
python setup.py --create-stubs
```

## 2. Full Compile and Install Test

Run the following command to force pip to completely compile the MyPyC extensions and reinstall the package from the local source directory without caching. This verifies the full build pipeline.

**On Windows:**

CD into the project root, then run:

```powershell
py -m pip install . --no-deps --no-cache-dir --force-reinstall -vv
```

**On Unix:**

CD into the project root, activate the `.venv` virtual environment, then run:

```bash
pip install . --no-deps --no-cache-dir --force-reinstall -vv
```

If any of these commands fail, inspect the verbose (`-vv`) output to debug MyPyC compilation errors or stub generation issues.
